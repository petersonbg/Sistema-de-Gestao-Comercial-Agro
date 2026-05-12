"""Configuração do Django Admin para orçamentos."""
from django.contrib import admin

from .models import Orcamento, OrcamentoItem


class OrcamentoItemInline(admin.TabularInline):
    model = OrcamentoItem
    extra = 0
    fields = ("empresa", "produto", "quantidade", "preco_unitario", "desconto", "subtotal")
    autocomplete_fields = ("empresa", "produto")


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "validade", "empresa", "cliente", "usuario", "status", "subtotal", "desconto", "total")
    search_fields = (
        "=id",
        "cliente__nome",
        "cliente__cpf_cnpj",
        "usuario__username",
        "empresa__nome_fantasia",
        "observacoes",
    )
    list_filter = ("status", "validade", "usuario")
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("empresa", "cliente", "usuario")
    inlines = (OrcamentoItemInline,)
    fieldsets = (
        ("Identificação", {"fields": ("empresa", "cliente", "usuario", "data", "validade", "status")}),
        ("Valores", {"fields": ("subtotal", "desconto", "total")}),
        ("Observações", {"fields": ("observacoes",)}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )


@admin.register(OrcamentoItem)
class OrcamentoItemAdmin(admin.ModelAdmin):
    list_display = ("orcamento", "produto", "empresa", "quantidade", "preco_unitario", "desconto", "subtotal")
    search_fields = ("=orcamento__id", "produto__nome", "produto__codigo_interno")
    list_filter = ("empresa", "produto")
    list_select_related = ("empresa", "orcamento", "produto")
