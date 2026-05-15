"""Views do módulo de estoque."""
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from core.crud_mixins import EmpresaAdministradorObrigatoriaMixin
from produtos.models import Produto

from .forms import EntradaLoteForm, EntradaSerialForm, EntradaSimplesForm, ProdutoEntradaForm
from .models import LoteEstoque, MovimentacaoEstoque, UnidadeIdentificada


class EntradaEstoqueView(EmpresaAdministradorObrigatoriaMixin, View):
    """Tela principal de entrada de estoque por tipo de controle do produto."""

    template_name = "estoque/entrada_estoque.html"
    form_classes = {
        Produto.TipoControleEstoque.SIMPLES: EntradaSimplesForm,
        Produto.TipoControleEstoque.LOTE: EntradaLoteForm,
        Produto.TipoControleEstoque.SERIAL: EntradaSerialForm,
    }

    def get(self, request, *args, **kwargs):
        produto = self.get_produto_selecionado()
        return self.render_form(produto=produto)

    def post(self, request, *args, **kwargs):
        produto = self.get_produto_selecionado()
        if not produto:
            messages.error(request, "Selecione um produto para registrar a entrada de estoque.")
            return redirect("estoque:entrada")

        form_class = self.get_form_class(produto)
        form = form_class(request.POST, empresa=self.get_empresa(), produto=produto)
        if not form.is_valid():
            messages.error(request, "Não foi possível registrar a entrada. Verifique os campos informados.")
            return self.render_form(produto=produto, entrada_form=form)

        with transaction.atomic():
            produto_bloqueado = Produto.objects.select_for_update().get(pk=produto.pk, empresa=self.get_empresa())
            if produto_bloqueado.tipo_controle_estoque == Produto.TipoControleEstoque.SIMPLES:
                self.registrar_entrada_simples(form, produto_bloqueado)
            elif produto_bloqueado.tipo_controle_estoque == Produto.TipoControleEstoque.LOTE:
                self.registrar_entrada_lote(form, produto_bloqueado)
            elif produto_bloqueado.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
                self.registrar_entrada_serial(form, produto_bloqueado)

        messages.success(request, "Entrada de estoque registrada com sucesso.")
        return redirect(f"{reverse('estoque:entrada')}?produto={produto.pk}")

    def get_produto_selecionado(self):
        """Retorna o produto selecionado na query string, limitado à empresa do usuário."""
        produto_id = self.request.GET.get("produto") or self.request.POST.get("produto")
        if not produto_id:
            return None
        return get_object_or_404(Produto, pk=produto_id, empresa=self.get_empresa(), ativo=True)

    def get_form_class(self, produto):
        """Seleciona o formulário adequado ao tipo de controle do produto."""
        return self.form_classes[produto.tipo_controle_estoque]

    def render_form(self, produto=None, entrada_form=None):
        """Renderiza a tela com seleção de produto e formulário específico."""
        produto_form = ProdutoEntradaForm(
            data={"produto": produto.pk} if produto else None,
            empresa=self.get_empresa(),
        )
        if produto and entrada_form is None:
            entrada_form = self.get_form_class(produto)(empresa=self.get_empresa(), produto=produto)

        return render(
            self.request,
            self.template_name,
            {
                "produto_form": produto_form,
                "produto": produto,
                "entrada_form": entrada_form,
            },
        )

    def registrar_entrada_simples(self, form, produto):
        """Registra entrada de produto com controle simples."""
        quantidade = form.cleaned_data["quantidade"]
        preco_custo = form.cleaned_data["preco_custo"]
        fornecedor = form.cleaned_data.get("fornecedor")
        observacao = form.cleaned_data.get("observacao", "")

        produto.estoque_atual += quantidade
        produto.preco_custo = preco_custo
        produto.save(update_fields=["estoque_atual", "preco_custo", "atualizado_em"])

        observacao_movimentacao = observacao
        if fornecedor:
            observacao_movimentacao = f"Fornecedor: {fornecedor}. {observacao}".strip()

        MovimentacaoEstoque.objects.create(
            empresa=self.get_empresa(),
            produto=produto,
            tipo_movimentacao=MovimentacaoEstoque.TipoMovimentacao.ENTRADA,
            quantidade=quantidade,
            usuario=self.request.user,
            observacao=observacao_movimentacao,
        )

    def registrar_entrada_lote(self, form, produto):
        """Registra entrada de produto com controle por lote."""
        quantidade = form.cleaned_data["quantidade"]
        preco_custo = form.cleaned_data["preco_custo"]
        lote = LoteEstoque.objects.create(
            empresa=self.get_empresa(),
            produto=produto,
            fornecedor=form.cleaned_data["fornecedor"],
            numero_lote=form.cleaned_data["numero_lote"],
            validade=form.cleaned_data["validade"],
            quantidade_inicial=quantidade,
            quantidade_atual=quantidade,
            preco_custo=preco_custo,
            data_entrada=timezone.localdate(),
        )

        produto.estoque_atual += quantidade
        produto.preco_custo = preco_custo
        produto.save(update_fields=["estoque_atual", "preco_custo", "atualizado_em"])

        MovimentacaoEstoque.objects.create(
            empresa=self.get_empresa(),
            produto=produto,
            tipo_movimentacao=MovimentacaoEstoque.TipoMovimentacao.ENTRADA,
            quantidade=quantidade,
            lote=lote,
            usuario=self.request.user,
            observacao=form.cleaned_data.get("observacao", ""),
        )

    def registrar_entrada_serial(self, form, produto):
        """Registra entrada de produto com controle por unidade identificada."""
        unidade = UnidadeIdentificada.objects.create(
            empresa=self.get_empresa(),
            produto=produto,
            fornecedor=form.cleaned_data["fornecedor"],
            numero_serie=form.cleaned_data.get("numero_serie", ""),
            chassi=form.cleaned_data.get("chassi", ""),
            modelo=form.cleaned_data.get("modelo", ""),
            cor=form.cleaned_data.get("cor", ""),
            ano_modelo=form.cleaned_data.get("ano_modelo"),
            ano_fabricacao=form.cleaned_data.get("ano_fabricacao"),
            preco_custo=form.cleaned_data["preco_custo"],
            preco_venda=form.cleaned_data.get("preco_venda") or produto.preco_venda,
            status=UnidadeIdentificada.Status.DISPONIVEL,
            observacoes=form.cleaned_data.get("observacoes", ""),
        )

        produto.estoque_atual += Decimal("1.000")
        produto.save(update_fields=["estoque_atual", "atualizado_em"])

        MovimentacaoEstoque.objects.create(
            empresa=self.get_empresa(),
            produto=produto,
            tipo_movimentacao=MovimentacaoEstoque.TipoMovimentacao.ENTRADA,
            quantidade=Decimal("1.000"),
            unidade_identificada=unidade,
            usuario=self.request.user,
            observacao=form.cleaned_data.get("observacao_movimentacao", ""),
        )
