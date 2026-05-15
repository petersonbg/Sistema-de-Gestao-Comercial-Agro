"""Views centrais do sistema."""
from django.contrib import messages
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from orcamentos.models import Orcamento
from produtos.models import Produto
from vendas.models import Venda

from .permissions import PERFIL_ADMINISTRADOR, PERFIL_VENDEDOR


def _filtrar_por_empresa(queryset, user):
    """Restringe dados por empresa para vendedores; administradores visualizam tudo."""
    if getattr(user, "perfil", None) == PERFIL_ADMINISTRADOR or user.is_superuser:
        return queryset

    empresa = getattr(user, "empresa", None)
    if empresa:
        return queryset.filter(empresa=empresa)

    return queryset.none()


@login_required
def dashboard(request):
    """Exibe a página inicial protegida do sistema com indicadores simples."""
    hoje = timezone.localdate()

    clientes = _filtrar_por_empresa(Cliente.objects.all(), request.user)
    produtos = _filtrar_por_empresa(Produto.objects.all(), request.user)
    vendas = _filtrar_por_empresa(Venda.objects.all(), request.user)
    orcamentos = _filtrar_por_empresa(Orcamento.objects.all(), request.user)

    cards = [
        {
            "title": "Total de clientes",
            "value": clientes.count(),
            "description": "Clientes cadastrados na base acessível.",
            "color": "success",
        },
        {
            "title": "Produtos ativos",
            "value": produtos.filter(ativo=True).count(),
            "description": "Produtos disponíveis para operação comercial.",
            "color": "primary",
        },
        {
            "title": "Estoque baixo",
            "value": produtos.filter(ativo=True, estoque_atual__lte=F("estoque_minimo")).count(),
            "description": "Produtos ativos no estoque mínimo ou abaixo dele.",
            "color": "warning",
        },
        {
            "title": "Vendas do dia",
            "value": vendas.filter(data__date=hoje).count(),
            "description": "Vendas registradas hoje.",
            "color": "info",
        },
        {
            "title": "Orçamentos abertos",
            "value": orcamentos.filter(status=Orcamento.Status.ABERTO).count(),
            "description": "Orçamentos aguardando aprovação.",
            "color": "secondary",
        },
    ]

    perfil_comercial = [PERFIL_ADMINISTRADOR, PERFIL_VENDEDOR]
    modules = [
        {
            "name": "Clientes",
            "description": "Cadastro e histórico de clientes.",
            "url": "clientes:list",
            "profiles": perfil_comercial,
        },
        {
            "name": "Produtos",
            "description": "Adubos, peças, triciclos e itens diversos.",
            "url": "produtos:produto_list",
            "profiles": perfil_comercial,
        },
        {
            "name": "Vendas",
            "description": "Venda balcão com baixa automática de estoque.",
            "url": "vendas:balcao",
            "profiles": perfil_comercial,
        },
        {
            "name": "Orçamentos",
            "description": "Propostas comerciais e negociações.",
            "url": "#",
            "profiles": perfil_comercial,
        },
        {
            "name": "Empresas",
            "description": "Dados da empresa e filiais.",
            "url": "#",
            "profiles": [PERFIL_ADMINISTRADOR],
        },
        {
            "name": "Fornecedores",
            "description": "Cadastro de fornecedores e parceiros.",
            "url": "fornecedores:list",
            "profiles": [PERFIL_ADMINISTRADOR],
        },
        {
            "name": "Estoque",
            "description": "Entradas, movimentações e disponibilidade de produtos.",
            "url": "estoque:entrada",
            "profiles": [PERFIL_ADMINISTRADOR],
        },
        {
            "name": "Financeiro",
            "description": "Contas a pagar, receber e fluxo de caixa.",
            "url": "#",
            "profiles": [PERFIL_ADMINISTRADOR],
        },
        {
            "name": "Relatórios",
            "description": "Indicadores comerciais e gerenciais.",
            "url": "#",
            "profiles": [PERFIL_ADMINISTRADOR],
        },
    ]
    modules = [
        module
        for module in modules
        if getattr(request.user, "perfil", None) in module["profiles"] or request.user.is_superuser
    ]
    for module in modules:
        if module["url"] != "#":
            module["url"] = reverse(module["url"])

    return render(request, "dashboard.html", {"cards": cards, "modules": modules})


@login_required
def logout_view(request):
    """Exibe confirmação de logout e encerra a sessão via POST."""
    if request.method == "POST":
        django_logout(request)
        messages.success(request, "Você saiu do sistema com segurança.")
        return render(request, "registration/logged_out.html")

    return render(request, "registration/logout.html")
