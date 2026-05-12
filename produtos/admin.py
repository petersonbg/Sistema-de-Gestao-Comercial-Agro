"""Configuração do Django Admin para produtos."""
from django.contrib import admin

from core.admin_permissions import AdminComercialMixin

from .models import Categoria, Marca, Produto


@admin.register(Categoria)
class CategoriaAdmin(AdminComercialMixin, admin.ModelAdmin):
    list_display = ("nome", "empresa", "ativo")
    search_fields = ("nome", "descricao", "empresa__nome_fantasia")
    list_filter = ("empresa", "ativo")


@admin.register(Marca)
class MarcaAdmin(AdminComercialMixin, admin.ModelAdmin):
    list_display = ("nome", "empresa", "ativo")
    search_fields = ("nome", "empresa__nome_fantasia")
    list_filter = ("empresa", "ativo")


@admin.register(Produto)
class ProdutoAdmin(AdminComercialMixin, admin.ModelAdmin):
    list_display = (
        "codigo_interno",
        "nome",
        "empresa",
        "categoria",
        "marca",
        "tipo_produto",
        "tipo_controle_estoque",
        "unidade_venda",
        "estoque_atual",
        "preco_venda",
        "ativo",
    )
    search_fields = (
        "nome",
        "descricao",
        "codigo_interno",
        "codigo_barras",
        "empresa__nome_fantasia",
        "categoria__nome",
        "marca__nome",
    )
    list_filter = ("empresa", "categoria", "tipo_produto", "tipo_controle_estoque", "ativo")
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("empresa", "categoria", "marca")
    fieldsets = (
        ("Identificação", {"fields": ("empresa", "categoria", "marca", "nome", "descricao", "ativo")}),
        ("Códigos", {"fields": ("codigo_interno", "codigo_barras")}),
        ("Classificação e controle", {"fields": ("tipo_produto", "tipo_controle_estoque")}),
        (
            "Venda e embalagem",
            {"fields": ("unidade_venda", "quantidade_por_embalagem", "unidade_referencia")},
        ),
        ("Preços", {"fields": ("preco_custo", "preco_venda")}),
        ("Estoque", {"fields": ("estoque_atual", "estoque_minimo")}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )
