"""Views do módulo de vendas."""
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView

from core.crud_mixins import EmpresaObrigatoriaMixin
from estoque.models import LoteEstoque, MovimentacaoEstoque, UnidadeIdentificada
from produtos.models import Produto

from .forms import AdicionarItemVendaForm, FinalizarVendaForm, ProdutoBuscaForm
from .models import Venda, VendaItem


CARRINHO_SESSION_KEY = "venda_balcao_carrinho"


class VendaBalcaoView(EmpresaObrigatoriaMixin, View):
    """Tela simples de venda balcão com carrinho em sessão."""

    template_name = "vendas/venda_balcao.html"

    def get(self, request, *args, **kwargs):
        return self.renderizar()

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "add_item":
            return self.adicionar_item()
        if action == "remove_item":
            return self.remover_item()
        if action == "clear_cart":
            return self.limpar_carrinho()
        if action == "finalize":
            return self.finalizar_venda()

        messages.error(request, "Ação inválida para a venda.")
        return redirect("vendas:balcao")

    def renderizar(self, add_form_errors=None, finalizar_form=None):
        busca_form = ProdutoBuscaForm(self.request.GET or None)
        produtos_encontrados = self.buscar_produtos(busca_form)
        produtos_forms = [
            {
                "produto": produto,
                "form": add_form_errors if add_form_errors and add_form_errors.produto == produto else AdicionarItemVendaForm(
                    empresa=self.get_empresa(),
                    produto=produto,
                ),
            }
            for produto in produtos_encontrados
        ]
        carrinho = self.get_carrinho_detalhado()
        finalizar_form = finalizar_form or FinalizarVendaForm(empresa=self.get_empresa())

        return render(
            self.request,
            self.template_name,
            {
                "busca_form": busca_form,
                "produtos_forms": produtos_forms,
                "carrinho": carrinho,
                "finalizar_form": finalizar_form,
            },
        )

    def buscar_produtos(self, busca_form):
        """Busca produtos ativos por nome, código interno ou código de barras."""
        queryset = Produto.objects.filter(empresa=self.get_empresa(), ativo=True).select_related("categoria", "marca")
        if busca_form.is_valid():
            termo = busca_form.cleaned_data.get("q", "").strip()
            if termo:
                return queryset.filter(
                    Q(nome__icontains=termo)
                    | Q(codigo_interno__icontains=termo)
                    | Q(codigo_barras__icontains=termo)
                )[:20]
        return queryset.none()

    def adicionar_item(self):
        """Adiciona item ao carrinho da sessão."""
        produto = get_object_or_404(
            Produto,
            pk=self.request.POST.get("produto_id"),
            empresa=self.get_empresa(),
            ativo=True,
        )
        form = AdicionarItemVendaForm(self.request.POST, empresa=self.get_empresa(), produto=produto)
        if not form.is_valid():
            messages.error(self.request, "Não foi possível adicionar o item. Verifique quantidade, desconto e unidade.")
            return self.renderizar(add_form_errors=form)

        item = {
            "produto_id": produto.pk,
            "quantidade": str(form.cleaned_data["quantidade"]),
            "desconto": str(form.cleaned_data["desconto"] or Decimal("0.00")),
            "unidade_identificada_id": None,
        }
        unidade = form.cleaned_data.get("unidade_identificada")
        if produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
            if self.unidade_ja_no_carrinho(unidade.pk):
                messages.error(self.request, "Esta unidade identificada já está no carrinho.")
                return redirect(f"{reverse('vendas:balcao')}?q={produto.codigo_interno}")
            item["unidade_identificada_id"] = unidade.pk

        carrinho = self.get_carrinho()
        carrinho.append(item)
        self.salvar_carrinho(carrinho)
        messages.success(self.request, "Item adicionado à venda.")
        return redirect(f"{reverse('vendas:balcao')}?q={produto.codigo_interno}")

    def remover_item(self):
        """Remove um item do carrinho pelo índice."""
        carrinho = self.get_carrinho()
        try:
            indice = int(self.request.POST.get("index"))
            carrinho.pop(indice)
        except (TypeError, ValueError, IndexError):
            messages.error(self.request, "Item não encontrado no carrinho.")
        else:
            self.salvar_carrinho(carrinho)
            messages.success(self.request, "Item removido do carrinho.")
        return redirect("vendas:balcao")

    def limpar_carrinho(self):
        """Limpa todos os itens da venda atual."""
        self.salvar_carrinho([])
        messages.success(self.request, "Carrinho limpo com sucesso.")
        return redirect("vendas:balcao")

    def finalizar_venda(self):
        """Finaliza venda com baixa de estoque atômica."""
        carrinho = self.get_carrinho()
        form = FinalizarVendaForm(self.request.POST, empresa=self.get_empresa())
        if not carrinho:
            messages.error(self.request, "Adicione pelo menos um item antes de finalizar a venda.")
            return self.renderizar(finalizar_form=form)
        if not form.is_valid():
            messages.error(self.request, "Não foi possível finalizar a venda. Verifique os dados de pagamento.")
            return self.renderizar(finalizar_form=form)

        try:
            with transaction.atomic():
                venda = self.criar_venda_e_baixar_estoque(carrinho, form)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0] if hasattr(exc, "messages") else str(exc))
            return self.renderizar(finalizar_form=form)

        self.salvar_carrinho([])
        messages.success(self.request, f"Venda #{venda.pk} finalizada com sucesso.")
        return redirect("vendas:confirmacao", pk=venda.pk)

    def criar_venda_e_baixar_estoque(self, carrinho, form):
        """Cria venda, itens, movimentações e baixa estoque em uma transação."""
        itens_preparados = [self.preparar_item(item) for item in carrinho]
        subtotal = self.moeda(sum(item["subtotal"] for item in itens_preparados))
        desconto_total = form.cleaned_data["desconto"] or Decimal("0.00")
        if desconto_total > subtotal:
            raise ValidationError("Desconto total não pode ser maior que o subtotal da venda.")
        total = self.moeda(subtotal - desconto_total)
        if total < 0:
            raise ValidationError("Total da venda não pode ser negativo.")

        venda = Venda.objects.create(
            empresa=self.get_empresa(),
            cliente=form.cleaned_data.get("cliente"),
            usuario=self.request.user,
            subtotal=subtotal,
            desconto=desconto_total,
            total=total,
            forma_pagamento=form.cleaned_data["forma_pagamento"],
            status=Venda.Status.FINALIZADA,
            observacoes=form.cleaned_data.get("observacoes", ""),
        )

        for item in itens_preparados:
            produto = item["produto"]
            if produto.tipo_controle_estoque == Produto.TipoControleEstoque.SIMPLES:
                self.baixar_produto_simples(venda, item)
            elif produto.tipo_controle_estoque == Produto.TipoControleEstoque.LOTE:
                self.baixar_produto_lote(venda, item)
            elif produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
                self.baixar_produto_serial(venda, item)

        return venda

    def preparar_item(self, item):
        """Valida dados básicos do item e calcula subtotal com desconto."""
        try:
            produto = Produto.objects.select_for_update().get(
                pk=item["produto_id"],
                empresa=self.get_empresa(),
            )
        except Produto.DoesNotExist as exc:
            raise ValidationError("Produto do carrinho não foi encontrado para esta empresa.") from exc
        if not produto.ativo:
            raise ValidationError(f"Produto inativo não pode ser vendido: {produto.nome}.")

        quantidade = Decimal(item["quantidade"])
        desconto = Decimal(item.get("desconto") or "0.00")
        if quantidade <= 0:
            raise ValidationError(f"Quantidade inválida para {produto.nome}.")
        if desconto < 0:
            raise ValidationError(f"Desconto inválido para {produto.nome}.")
        if produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
            quantidade = Decimal("1.000")

        subtotal_bruto = self.moeda(produto.preco_venda * quantidade)
        if desconto > subtotal_bruto:
            raise ValidationError(f"Desconto do item não pode superar o subtotal de {produto.nome}.")

        return {
            "produto": produto,
            "quantidade": quantidade,
            "preco_unitario": produto.preco_venda,
            "desconto": desconto,
            "subtotal": self.moeda(subtotal_bruto - desconto),
            "unidade_identificada_id": item.get("unidade_identificada_id"),
        }

    def baixar_produto_simples(self, venda, item):
        """Baixa estoque de produto simples."""
        produto = item["produto"]
        quantidade = item["quantidade"]
        if produto.estoque_atual < quantidade:
            raise ValidationError(f"Estoque insuficiente para {produto.nome}.")

        produto.estoque_atual -= quantidade
        produto.save(update_fields=["estoque_atual", "atualizado_em"])
        venda_item = VendaItem.objects.create(
            empresa=self.get_empresa(),
            venda=venda,
            produto=produto,
            quantidade=quantidade,
            preco_unitario=item["preco_unitario"],
            desconto=item["desconto"],
            subtotal=item["subtotal"],
        )
        self.registrar_movimentacao(venda_item, quantidade)

    def baixar_produto_lote(self, venda, item):
        """Baixa estoque de produto por lote usando FEFO."""
        produto = item["produto"]
        quantidade_restante = item["quantidade"]
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

        desconto_restante = item["desconto"]
        for lote in lotes:
            if quantidade_restante <= 0:
                break
            quantidade_baixa = min(quantidade_restante, lote.quantidade_atual)
            lote.quantidade_atual -= quantidade_baixa
            lote.save(update_fields=["quantidade_atual"])

            subtotal_bruto = self.moeda(item["preco_unitario"] * quantidade_baixa)
            if quantidade_baixa == quantidade_restante:
                desconto_lote = desconto_restante
            else:
                desconto_lote = self.moeda(min(desconto_restante, item["desconto"] * quantidade_baixa / item["quantidade"]))
            desconto_restante = self.moeda(desconto_restante - desconto_lote)
            subtotal_lote = self.moeda(subtotal_bruto - desconto_lote)

            venda_item = VendaItem.objects.create(
                empresa=self.get_empresa(),
                venda=venda,
                produto=produto,
                lote=lote,
                quantidade=quantidade_baixa,
                preco_unitario=item["preco_unitario"],
                desconto=desconto_lote,
                subtotal=subtotal_lote,
            )
            self.registrar_movimentacao(venda_item, quantidade_baixa)
            quantidade_restante -= quantidade_baixa

    def baixar_produto_serial(self, venda, item):
        """Baixa estoque de produto serial e marca unidade como vendida."""
        produto = item["produto"]
        if not item.get("unidade_identificada_id"):
            raise ValidationError(f"Selecione uma unidade identificada para {produto.nome}.")
        try:
            unidade = UnidadeIdentificada.objects.select_for_update().get(
                pk=item["unidade_identificada_id"],
                empresa=self.get_empresa(),
                produto=produto,
            )
        except UnidadeIdentificada.DoesNotExist as exc:
            raise ValidationError(f"Unidade identificada não encontrada para {produto.nome}.") from exc
        if unidade.status != UnidadeIdentificada.Status.DISPONIVEL:
            raise ValidationError(f"Unidade {unidade} não está disponível para venda.")
        if produto.estoque_atual < Decimal("1.000"):
            raise ValidationError(f"Estoque insuficiente para {produto.nome}.")

        unidade.status = UnidadeIdentificada.Status.VENDIDO
        unidade.save(update_fields=["status", "atualizado_em"])
        produto.estoque_atual -= Decimal("1.000")
        produto.save(update_fields=["estoque_atual", "atualizado_em"])

        venda_item = VendaItem.objects.create(
            empresa=self.get_empresa(),
            venda=venda,
            produto=produto,
            unidade_identificada=unidade,
            quantidade=Decimal("1.000"),
            preco_unitario=item["preco_unitario"],
            desconto=item["desconto"],
            subtotal=item["subtotal"],
        )
        self.registrar_movimentacao(venda_item, Decimal("1.000"))

    def registrar_movimentacao(self, venda_item, quantidade):
        """Registra movimentação de saída vinculada a um item de venda."""
        MovimentacaoEstoque.objects.create(
            empresa=self.get_empresa(),
            produto=venda_item.produto,
            tipo_movimentacao=MovimentacaoEstoque.TipoMovimentacao.SAIDA,
            quantidade=quantidade,
            lote=venda_item.lote,
            unidade_identificada=venda_item.unidade_identificada,
            usuario=self.request.user,
            observacao=f"Venda #{venda_item.venda_id}",
        )

    def get_carrinho(self):
        """Retorna o carrinho salvo na sessão."""
        return list(self.request.session.get(CARRINHO_SESSION_KEY, []))

    def salvar_carrinho(self, carrinho):
        """Salva o carrinho na sessão."""
        self.request.session[CARRINHO_SESSION_KEY] = carrinho
        self.request.session.modified = True

    def unidade_ja_no_carrinho(self, unidade_id):
        """Evita duplicar unidade serial no mesmo carrinho."""
        return any(item.get("unidade_identificada_id") == unidade_id for item in self.get_carrinho())

    def get_carrinho_detalhado(self):
        """Retorna itens do carrinho com dados do produto para exibição."""
        itens = []
        subtotal = Decimal("0.00")
        for index, item in enumerate(self.get_carrinho()):
            try:
                produto = Produto.objects.get(pk=item["produto_id"], empresa=self.get_empresa())
            except Produto.DoesNotExist:
                continue
            quantidade = Decimal(item["quantidade"])
            desconto = Decimal(item.get("desconto") or "0.00")
            if produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
                quantidade = Decimal("1.000")
            subtotal_item = self.moeda(produto.preco_venda * quantidade - desconto)
            unidade = None
            if item.get("unidade_identificada_id"):
                unidade = UnidadeIdentificada.objects.filter(
                    pk=item["unidade_identificada_id"],
                    empresa=self.get_empresa(),
                ).first()
            subtotal += subtotal_item
            itens.append(
                {
                    "index": index,
                    "produto": produto,
                    "quantidade": quantidade,
                    "preco_unitario": produto.preco_venda,
                    "desconto": desconto,
                    "subtotal": subtotal_item,
                    "unidade": unidade,
                }
            )
        return {"itens": itens, "subtotal": subtotal}

    @staticmethod
    def moeda(valor):
        """Arredonda valores monetários para duas casas decimais."""
        return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class VendaConfirmacaoView(EmpresaObrigatoriaMixin, DetailView):
    """Confirmação da venda finalizada."""

    model = Venda
    template_name = "vendas/venda_confirmacao.html"
    context_object_name = "venda"

    def get_queryset(self):
        return Venda.objects.filter(empresa=self.request.user.empresa).select_related("cliente", "usuario")
