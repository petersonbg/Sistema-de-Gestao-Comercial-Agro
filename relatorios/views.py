"""Views dos relatórios básicos do sistema."""
from django.db.models import F, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from core.crud_mixins import EmpresaAdministradorObrigatoriaMixin
from estoque.models import LoteEstoque
from produtos.models import Produto
from vendas.models import Venda, VendaItem

from .forms import PeriodoForm


class RelatorioBaseView(EmpresaAdministradorObrigatoriaMixin, TemplateView):
    """Base para relatórios restritos à empresa do usuário logado."""

    titulo = "Relatórios"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = self.titulo
        return context


class RelatoriosIndexView(RelatorioBaseView):
    """Página inicial com atalhos para os relatórios."""

    template_name = "relatorios/index.html"
    titulo = "Relatórios"


class VendasDiaView(RelatorioBaseView):
    """Relatório das vendas do dia atual."""

    template_name = "relatorios/vendas_dia.html"
    titulo = "Vendas do dia"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        vendas = Venda.objects.filter(empresa=self.get_empresa(), data__date=hoje).select_related("cliente", "usuario")
        context.update({"data_referencia": hoje, "vendas": vendas})
        return context


class VendasPeriodoView(RelatorioBaseView):
    """Relatório de vendas com filtro por período e totalizadores."""

    template_name = "relatorios/vendas_periodo.html"
    titulo = "Vendas por período"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PeriodoForm(self.request.GET or None)
        form.is_valid()
        data_inicial, data_final = form.periodo()
        vendas = Venda.objects.filter(
            empresa=self.get_empresa(),
            data__date__gte=data_inicial,
            data__date__lte=data_final,
        ).select_related("cliente", "usuario")
        vendas_finalizadas = vendas.filter(status=Venda.Status.FINALIZADA)
        total_geral = vendas_finalizadas.aggregate(total=Sum("total"))["total"] or 0
        formas_pagamento = dict(Venda.FormaPagamento.choices)
        totais_pagamento = [
            {**item, "forma_pagamento_display": formas_pagamento.get(item["forma_pagamento"], item["forma_pagamento"])}
            for item in vendas_finalizadas.values("forma_pagamento").annotate(total=Sum("total")).order_by("forma_pagamento")
        ]
        context.update(
            {
                "form": form,
                "data_inicial": data_inicial,
                "data_final": data_final,
                "vendas": vendas,
                "total_geral": total_geral,
                "totais_pagamento": totais_pagamento,
            }
        )
        return context


class ProdutosEstoqueBaixoView(RelatorioBaseView):
    """Relatório de produtos com estoque atual menor ou igual ao mínimo."""

    template_name = "relatorios/estoque_baixo.html"
    titulo = "Produtos com estoque baixo"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produtos = Produto.objects.filter(
            empresa=self.get_empresa(),
            ativo=True,
            estoque_atual__lte=F("estoque_minimo"),
        ).select_related("categoria", "marca")
        context["produtos"] = produtos
        return context


class ProdutosProximosVencimentoView(RelatorioBaseView):
    """Relatório de lotes que vencem em até 90 dias."""

    template_name = "relatorios/proximos_vencimento.html"
    titulo = "Produtos próximos do vencimento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        limite = hoje + timezone.timedelta(days=90)
        lotes = LoteEstoque.objects.filter(
            empresa=self.get_empresa(),
            ativo=True,
            quantidade_atual__gt=0,
            validade__gte=hoje,
            validade__lte=limite,
        ).select_related("produto", "fornecedor")
        context.update({"lotes": lotes, "data_inicial": hoje, "data_limite": limite})
        return context


class ProdutosVencidosView(RelatorioBaseView):
    """Relatório de lotes vencidos ainda com saldo."""

    template_name = "relatorios/vencidos.html"
    titulo = "Produtos vencidos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        lotes = LoteEstoque.objects.filter(
            empresa=self.get_empresa(),
            ativo=True,
            quantidade_atual__gt=0,
            validade__lt=hoje,
        ).select_related("produto", "fornecedor")
        context.update({"lotes": lotes, "data_referencia": hoje})
        return context


class ProdutosMaisVendidosView(RelatorioBaseView):
    """Relatório de produtos mais vendidos por período."""

    template_name = "relatorios/mais_vendidos.html"
    titulo = "Produtos mais vendidos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PeriodoForm(self.request.GET or None)
        form.is_valid()
        data_inicial, data_final = form.periodo()
        produtos = (
            VendaItem.objects.filter(
                empresa=self.get_empresa(),
                venda__status=Venda.Status.FINALIZADA,
                venda__data__date__gte=data_inicial,
                venda__data__date__lte=data_final,
            )
            .values("produto__id", "produto__nome", "produto__codigo_interno")
            .annotate(quantidade_vendida=Sum("quantidade"), valor_total=Sum("subtotal"))
            .order_by("-quantidade_vendida", "produto__nome")
        )
        context.update(
            {
                "form": form,
                "data_inicial": data_inicial,
                "data_final": data_final,
                "produtos": produtos,
            }
        )
        return context
