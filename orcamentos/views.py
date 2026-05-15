"""Views do módulo de orçamentos."""
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from core.crud_mixins import EmpresaObrigatoriaMixin
from core.pdf import get_empresa_logo_url, render_pdf_response
from estoque.models import LoteEstoque, MovimentacaoEstoque, UnidadeIdentificada
from produtos.models import Produto
from vendas.models import Venda, VendaItem

from .forms import ConverterOrcamentoForm, OrcamentoFiltroForm, OrcamentoForm, OrcamentoItemFormSet
from .models import Orcamento, OrcamentoItem


class OrcamentoQuerysetMixin(EmpresaObrigatoriaMixin):
    """Restringe orçamentos à empresa do usuário logado."""

    model = Orcamento

    def get_queryset(self):
        return Orcamento.objects.filter(empresa=self.get_empresa()).select_related("cliente", "usuario")

    def atualizar_vencidos(self):
        """Marca orçamentos expirados como vencidos sem baixar estoque."""
        Orcamento.objects.filter(
            empresa=self.get_empresa(),
            status__in=[Orcamento.Status.ABERTO, Orcamento.Status.APROVADO],
            validade__lt=timezone.localdate(),
        ).update(status=Orcamento.Status.VENCIDO, atualizado_em=timezone.now())

    @staticmethod
    def usuario_eh_administrador(user):
        """Retorna se o usuário pode autorizar conversões excepcionais."""
        return user.is_superuser or getattr(user, "perfil", None) == "administrador"


class OrcamentoListView(OrcamentoQuerysetMixin, ListView):
    """Lista orçamentos com filtros por status e cliente."""

    template_name = "orcamentos/orcamento_list.html"
    context_object_name = "orcamentos"
    paginate_by = 10

    def get_queryset(self):
        self.atualizar_vencidos()
        queryset = super().get_queryset()
        self.filtro_form = OrcamentoFiltroForm(self.request.GET or None, empresa=self.get_empresa())
        if self.filtro_form.is_valid():
            status = self.filtro_form.cleaned_data.get("status")
            cliente = self.filtro_form.cleaned_data.get("cliente")
            if status:
                queryset = queryset.filter(status=status)
            if cliente:
                queryset = queryset.filter(cliente=cliente)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtro_form"] = getattr(self, "filtro_form", OrcamentoFiltroForm(empresa=self.get_empresa()))
        return context


class OrcamentoCreateView(OrcamentoQuerysetMixin, CreateView):
    """Cria orçamento com cliente obrigatório, validade e itens."""

    form_class = OrcamentoForm
    template_name = "orcamentos/orcamento_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["item_formset"] = OrcamentoItemFormSet(self.request.POST, empresa=self.get_empresa())
        else:
            context["item_formset"] = OrcamentoItemFormSet(empresa=self.get_empresa())
        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        item_formset = context["item_formset"]
        if not item_formset.is_valid():
            messages.error(self.request, "Não foi possível salvar o orçamento. Verifique os itens informados.")
            return self.form_invalid(form)

        with transaction.atomic():
            orcamento = form.save(commit=False)
            orcamento.empresa = self.get_empresa()
            orcamento.usuario = self.request.user
            orcamento.status = Orcamento.Status.ABERTO
            orcamento.subtotal = Decimal("0.00")
            orcamento.total = Decimal("0.00")
            orcamento.save()

            subtotal_itens = self.salvar_itens(orcamento, item_formset)
            if orcamento.desconto > subtotal_itens:
                form.add_error("desconto", "Desconto total não pode ser maior que o subtotal dos itens.")
                transaction.set_rollback(True)
                return self.form_invalid(form)
            orcamento.subtotal = subtotal_itens
            orcamento.total = self.moeda(subtotal_itens - orcamento.desconto)
            orcamento.save(update_fields=["subtotal", "total", "atualizado_em"])

        self.object = orcamento
        messages.success(self.request, "Orçamento salvo com sucesso.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível salvar o orçamento. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("orcamentos:detail", kwargs={"pk": self.object.pk})

    def salvar_itens(self, orcamento, item_formset):
        """Persiste itens do orçamento calculando preços e descontos."""
        subtotal_itens = Decimal("0.00")
        for item_form in item_formset.forms:
            if not item_form.cleaned_data or item_form.cleaned_data.get("DELETE"):
                continue
            produto = item_form.cleaned_data["produto"]
            quantidade = item_form.cleaned_data["quantidade"]
            if produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
                quantidade = Decimal("1.000")
            desconto = item_form.cleaned_data.get("desconto") or Decimal("0.00")
            subtotal_item = self.moeda(produto.preco_venda * quantidade - desconto)
            OrcamentoItem.objects.create(
                empresa=self.get_empresa(),
                orcamento=orcamento,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=produto.preco_venda,
                desconto=desconto,
                subtotal=subtotal_item,
            )
            subtotal_itens += subtotal_item
        return self.moeda(subtotal_itens)

    @staticmethod
    def moeda(valor):
        """Arredonda valores monetários para duas casas decimais."""
        return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class OrcamentoDetailView(OrcamentoQuerysetMixin, DetailView):
    """Exibe a visualização do orçamento."""

    template_name = "orcamentos/orcamento_detail.html"
    context_object_name = "orcamento"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("itens__produto")

    def get_object(self, queryset=None):
        orcamento = super().get_object(queryset)
        if (
            orcamento.status in [Orcamento.Status.ABERTO, Orcamento.Status.APROVADO]
            and orcamento.validade < timezone.localdate()
        ):
            orcamento.status = Orcamento.Status.VENCIDO
            orcamento.save(update_fields=["status", "atualizado_em"])
        return orcamento

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["converter_form"] = ConverterOrcamentoForm()
        context["pode_autorizar_vencido"] = self.usuario_eh_administrador(self.request.user)
        return context


class OrcamentoPdfView(OrcamentoQuerysetMixin, DetailView):
    """Gera a visualização do orçamento em PDF para abertura inline no navegador."""

    template_name = "orcamentos/pdf/orcamento.html"
    context_object_name = "orcamento"

    def get_queryset(self):
        return super().get_queryset().select_related("empresa", "cliente", "usuario").prefetch_related("itens__produto")

    def get(self, request, *args, **kwargs):
        orcamento = self.get_object()
        context = {
            "orcamento": orcamento,
            "empresa": orcamento.empresa,
            "cliente": orcamento.cliente,
            "logo_url": get_empresa_logo_url(orcamento.empresa),
        }
        return render_pdf_response(
            request,
            "orcamentos/pdf/orcamento.html",
            context,
            f"orcamento-{orcamento.pk}.pdf",
        )


class OrcamentoCancelarView(OrcamentoQuerysetMixin, View):
    """Cancela orçamento que ainda não foi convertido."""

    def post(self, request, *args, **kwargs):
        orcamento = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        if orcamento.status == Orcamento.Status.CONVERTIDO:
            messages.error(request, "Orçamento convertido não pode ser cancelado.")
            return redirect("orcamentos:detail", pk=orcamento.pk)
        if orcamento.status == Orcamento.Status.CANCELADO:
            messages.info(request, "Orçamento já estava cancelado.")
            return redirect("orcamentos:detail", pk=orcamento.pk)
        orcamento.status = Orcamento.Status.CANCELADO
        orcamento.save(update_fields=["status", "atualizado_em"])
        messages.success(request, "Orçamento cancelado com sucesso.")
        return redirect("orcamentos:detail", pk=orcamento.pk)


class OrcamentoConverterView(OrcamentoQuerysetMixin, View):
    """Converte orçamento em venda validando estoque no momento da conversão."""

    def post(self, request, *args, **kwargs):
        orcamento = get_object_or_404(self.get_queryset().prefetch_related("itens__produto"), pk=kwargs["pk"])
        form = ConverterOrcamentoForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Informe a forma de pagamento para converter o orçamento.")
            return redirect("orcamentos:detail", pk=orcamento.pk)

        try:
            with transaction.atomic():
                venda = self.converter_orcamento(orcamento.pk, form.cleaned_data["forma_pagamento"])
        except ValidationError as exc:
            messages.error(request, exc.messages[0] if hasattr(exc, "messages") else str(exc))
            return redirect("orcamentos:detail", pk=orcamento.pk)

        messages.success(request, f"Orçamento #{orcamento.pk} convertido na venda #{venda.pk}.")
        return redirect("vendas:confirmacao", pk=venda.pk)

    def converter_orcamento(self, orcamento_id, forma_pagamento):
        """Executa a conversão de forma atômica e idempotente."""
        orcamento = (
            Orcamento.objects.select_for_update()
            .select_related("cliente")
            .prefetch_related("itens__produto")
            .get(pk=orcamento_id, empresa=self.get_empresa())
        )
        self.validar_conversao(orcamento)

        venda = Venda.objects.create(
            empresa=self.get_empresa(),
            cliente=orcamento.cliente,
            usuario=self.request.user,
            subtotal=orcamento.subtotal,
            desconto=orcamento.desconto,
            total=orcamento.total,
            forma_pagamento=forma_pagamento,
            status=Venda.Status.FINALIZADA,
            observacoes=f"Convertida do orçamento #{orcamento.pk}.\n{orcamento.observacoes}".strip(),
        )

        for item in orcamento.itens.select_related("produto"):
            self.baixar_item(venda, item)

        orcamento.status = Orcamento.Status.CONVERTIDO
        orcamento.save(update_fields=["status", "atualizado_em"])
        return venda

    def validar_conversao(self, orcamento):
        """Valida status, vencimento e existência de itens antes de converter."""
        if orcamento.status == Orcamento.Status.CONVERTIDO:
            raise ValidationError("Orçamento já convertido não pode ser convertido novamente.")
        if orcamento.status == Orcamento.Status.CANCELADO:
            raise ValidationError("Orçamento cancelado não pode ser convertido.")
        if orcamento.status == Orcamento.Status.VENCIDO and not self.usuario_eh_administrador(self.request.user):
            raise ValidationError("Orçamento vencido só pode ser convertido por um administrador.")
        if orcamento.validade < timezone.localdate() and not self.usuario_eh_administrador(self.request.user):
            orcamento.status = Orcamento.Status.VENCIDO
            orcamento.save(update_fields=["status", "atualizado_em"])
            raise ValidationError("Orçamento vencido só pode ser convertido por um administrador.")
        if not orcamento.itens.exists():
            raise ValidationError("Orçamento sem itens não pode ser convertido.")

    def baixar_item(self, venda, item):
        """Baixa estoque seguindo o tipo de controle do produto."""
        produto = Produto.objects.select_for_update().get(pk=item.produto_id, empresa=self.get_empresa())
        if produto.tipo_controle_estoque == Produto.TipoControleEstoque.LOTE:
            self.baixar_produto_lote(venda, item, produto)
        elif produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
            self.baixar_produto_serial(venda, item, produto)
        else:
            self.baixar_produto_simples(venda, item, produto)

    def baixar_produto_simples(self, venda, item, produto):
        """Baixa estoque de produto simples."""
        if produto.estoque_atual < item.quantidade:
            raise ValidationError(f"Estoque insuficiente para {produto.nome}.")
        produto.estoque_atual -= item.quantidade
        produto.save(update_fields=["estoque_atual", "atualizado_em"])
        venda_item = self.criar_venda_item(venda, item, quantidade=item.quantidade)
        self.registrar_movimentacao(venda_item, item.quantidade)

    def baixar_produto_lote(self, venda, item, produto):
        """Baixa estoque de produto por lote usando FEFO."""
        quantidade_restante = item.quantidade
        lotes = LoteEstoque.objects.select_for_update().filter(
            empresa=self.get_empresa(),
            produto=produto,
            ativo=True,
            validade__gte=timezone.localdate(),
            quantidade_atual__gt=0,
        ).order_by("validade", "data_entrada", "numero_lote")

        quantidade_disponivel = sum(lote.quantidade_atual for lote in lotes)
        if quantidade_disponivel < quantidade_restante or produto.estoque_atual < quantidade_restante:
            raise ValidationError(f"Estoque por lote insuficiente ou vencido para {produto.nome}.")

        produto.estoque_atual -= quantidade_restante
        produto.save(update_fields=["estoque_atual", "atualizado_em"])

        desconto_restante = item.desconto
        quantidade_original = item.quantidade
        for lote in lotes:
            if quantidade_restante <= 0:
                break
            quantidade_baixa = min(quantidade_restante, lote.quantidade_atual)
            lote.quantidade_atual -= quantidade_baixa
            lote.save(update_fields=["quantidade_atual"])

            subtotal_bruto = self.moeda(item.preco_unitario * quantidade_baixa)
            if quantidade_baixa == quantidade_restante:
                desconto_lote = desconto_restante
            else:
                desconto_lote = self.moeda(min(desconto_restante, item.desconto * quantidade_baixa / quantidade_original))
            desconto_restante = self.moeda(desconto_restante - desconto_lote)
            subtotal_lote = self.moeda(subtotal_bruto - desconto_lote)

            venda_item = self.criar_venda_item(
                venda,
                item,
                quantidade=quantidade_baixa,
                lote=lote,
                desconto=desconto_lote,
                subtotal=subtotal_lote,
            )
            self.registrar_movimentacao(venda_item, quantidade_baixa)
            quantidade_restante -= quantidade_baixa

    def baixar_produto_serial(self, venda, item, produto):
        """Baixa uma unidade serial disponível no momento da conversão."""
        if produto.estoque_atual < Decimal("1.000"):
            raise ValidationError(f"Estoque insuficiente para {produto.nome}.")
        unidade = (
            UnidadeIdentificada.objects.select_for_update()
            .filter(empresa=self.get_empresa(), produto=produto, status=UnidadeIdentificada.Status.DISPONIVEL)
            .order_by("chassi", "numero_serie", "id")
            .first()
        )
        if not unidade:
            raise ValidationError(f"Não há unidade identificada disponível para {produto.nome}.")

        unidade.status = UnidadeIdentificada.Status.VENDIDO
        unidade.save(update_fields=["status", "atualizado_em"])
        produto.estoque_atual -= Decimal("1.000")
        produto.save(update_fields=["estoque_atual", "atualizado_em"])

        venda_item = self.criar_venda_item(venda, item, quantidade=Decimal("1.000"), unidade_identificada=unidade)
        self.registrar_movimentacao(venda_item, Decimal("1.000"))

    def criar_venda_item(self, venda, item, quantidade, lote=None, unidade_identificada=None, desconto=None, subtotal=None):
        """Cria item de venda derivado do item de orçamento."""
        return VendaItem.objects.create(
            empresa=self.get_empresa(),
            venda=venda,
            produto=item.produto,
            lote=lote,
            unidade_identificada=unidade_identificada,
            quantidade=quantidade,
            preco_unitario=item.preco_unitario,
            desconto=item.desconto if desconto is None else desconto,
            subtotal=item.subtotal if subtotal is None else subtotal,
        )

    def registrar_movimentacao(self, venda_item, quantidade):
        """Registra saída de estoque vinculada à venda convertida."""
        MovimentacaoEstoque.objects.create(
            empresa=self.get_empresa(),
            produto=venda_item.produto,
            tipo_movimentacao=MovimentacaoEstoque.TipoMovimentacao.SAIDA,
            quantidade=quantidade,
            lote=venda_item.lote,
            unidade_identificada=venda_item.unidade_identificada,
            usuario=self.request.user,
            observacao=f"Venda #{venda_item.venda_id} convertida de orçamento",
        )

    @staticmethod
    def moeda(valor):
        """Arredonda valores monetários para duas casas decimais."""
        return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
