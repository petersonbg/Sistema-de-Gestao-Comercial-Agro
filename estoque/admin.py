"""Configuração do Django Admin para estoque."""
from django.contrib import admin

from .models import LoteEstoque, MovimentacaoEstoque, UnidadeIdentificada


@admin.register(LoteEstoque)
class LoteEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "numero_lote",
        "produto",
        "empresa",
        "fornecedor",
        "validade",
        "quantidade_inicial",
        "quantidade_atual",
        "preco_custo",
        "data_entrada",
        "ativo",
    )
    search_fields = ("numero_lote", "produto__nome", "produto__codigo_interno", "fornecedor__nome", "empresa__nome_fantasia")
    list_filter = ("validade", "fornecedor", "produto", "ativo")
    list_select_related = ("empresa", "produto", "fornecedor")
    fieldsets = (
        ("Produto e lote", {"fields": ("empresa", "produto", "fornecedor", "numero_lote", "ativo")}),
        ("Validade e entrada", {"fields": ("validade", "data_entrada")}),
        ("Quantidades e custo", {"fields": ("quantidade_inicial", "quantidade_atual", "preco_custo")}),
    )


@admin.register(UnidadeIdentificada)
class UnidadeIdentificadaAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "empresa",
        "numero_serie",
        "chassi",
        "modelo",
        "cor",
        "ano_modelo",
        "status",
        "preco_venda",
    )
    search_fields = (
        "produto__nome",
        "produto__codigo_interno",
        "numero_serie",
        "chassi",
        "modelo",
        "cor",
        "fornecedor__nome",
        "empresa__nome_fantasia",
    )
    list_filter = ("status", "produto", "fornecedor", "empresa")
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("empresa", "produto", "fornecedor")
    fieldsets = (
        ("Produto", {"fields": ("empresa", "produto", "fornecedor", "status")}),
        ("Identificação", {"fields": ("numero_serie", "chassi", "modelo", "cor", "ano_modelo")}),
        ("Valores", {"fields": ("preco_custo", "preco_venda")}),
        ("Observações", {"fields": ("observacoes",)}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "tipo_movimentacao", "produto", "empresa", "quantidade", "lote", "unidade_identificada", "usuario")
    search_fields = (
        "produto__nome",
        "produto__codigo_interno",
        "lote__numero_lote",
        "unidade_identificada__numero_serie",
        "unidade_identificada__chassi",
        "usuario__username",
        "observacao",
    )
    list_filter = ("tipo_movimentacao", "empresa", "produto", "usuario", "criado_em")
    readonly_fields = ("criado_em",)
    list_select_related = ("empresa", "produto", "lote", "unidade_identificada", "usuario")
    fieldsets = (
        ("Movimentação", {"fields": ("empresa", "produto", "tipo_movimentacao", "quantidade")}),
        ("Controle específico", {"fields": ("lote", "unidade_identificada")}),
        ("Responsável e observação", {"fields": ("usuario", "observacao")}),
        ("Auditoria", {"fields": ("criado_em",)}),
    )
