"""URLs do app relatorios."""
from django.urls import path

from .views import (
    ProdutosEstoqueBaixoView,
    ProdutosMaisVendidosView,
    ProdutosProximosVencimentoView,
    ProdutosVencidosView,
    RelatoriosIndexView,
    VendasDiaView,
    VendasPeriodoView,
)

app_name = "relatorios"

urlpatterns = [
    path("", RelatoriosIndexView.as_view(), name="index"),
    path("vendas-dia/", VendasDiaView.as_view(), name="vendas_dia"),
    path("vendas-periodo/", VendasPeriodoView.as_view(), name="vendas_periodo"),
    path("estoque-baixo/", ProdutosEstoqueBaixoView.as_view(), name="estoque_baixo"),
    path("proximos-vencimento/", ProdutosProximosVencimentoView.as_view(), name="proximos_vencimento"),
    path("vencidos/", ProdutosVencidosView.as_view(), name="vencidos"),
    path("mais-vendidos/", ProdutosMaisVendidosView.as_view(), name="mais_vendidos"),
]
