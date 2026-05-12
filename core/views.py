"""Views centrais do sistema."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    """Exibe a página inicial protegida do sistema."""
    modules = [
        {"name": "Empresas", "description": "Dados da empresa e filiais.", "url": "#"},
        {"name": "Clientes", "description": "Cadastro e histórico de clientes.", "url": "#"},
        {"name": "Fornecedores", "description": "Cadastro de fornecedores e parceiros.", "url": "#"},
        {"name": "Produtos", "description": "Adubos, peças, triciclos e itens diversos.", "url": "#"},
        {"name": "Estoque", "description": "Movimentações e disponibilidade de produtos.", "url": "#"},
        {"name": "Vendas", "description": "Pedidos, vendas e emissão futura de documentos.", "url": "#"},
        {"name": "Orçamentos", "description": "Propostas comerciais e negociações.", "url": "#"},
        {"name": "Financeiro", "description": "Contas a pagar, receber e fluxo de caixa.", "url": "#"},
        {"name": "Relatórios", "description": "Indicadores comerciais e gerenciais.", "url": "#"},
    ]
    return render(request, "dashboard.html", {"modules": modules})
