"""Configuração do Django Admin para vendas."""
from django.contrib import admin

from core.admin_permissions import AdminComercialMixin

from .models import Venda, VendaItem


class VendaItemInline(admin.TabularInline):
    model = VendaItem
    extra = 0
    fields = ("empresa", "produto", "lote", "unidade_identificada", "quantidade", "preco_unitario", "desconto", "subtotal")
    autocomplete_fields = ("empresa", "produto", "lote", "unidade_identificada")


@admin.register(Venda)
class VendaAdmin(AdminComercialMixin, admin.ModelAdmin):
    list_display = ("id", "data", "empresa", "cliente", "usuario", "forma_pagamento", "status", "subtotal", "desconto", "total")
    search_fields = (
        "=id",
        "cliente__nome",
        "cliente__cpf_cnpj",
        "usuario__username",
        "empresa__nome_fantasia",
        "observacoes",
    )
    list_filter = ("status", "forma_pagamento", "data", "usuario")
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("empresa", "cliente", "usuario")
    inlines = (VendaItemInline,)
    fieldsets = (
        ("Identificação", {"fields": ("empresa", "cliente", "usuario", "data", "status")}),
        ("Pagamento", {"fields": ("forma_pagamento",)}),
        ("Valores", {"fields": ("subtotal", "desconto", "total")}),
        ("Observações", {"fields": ("observacoes",)}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )


@admin.register(VendaItem)
class VendaItemAdmin(AdminComercialMixin, admin.ModelAdmin):
    list_display = ("venda", "produto", "empresa", "quantidade", "preco_unitario", "desconto", "subtotal", "lote", "unidade_identificada")
    search_fields = (
        "=venda__id",
        "produto__nome",
        "produto__codigo_interno",
        "lote__numero_lote",
        "unidade_identificada__numero_serie",
        "unidade_identificada__chassi",
    )
    list_filter = ("empresa", "produto")
    list_select_related = ("empresa", "venda", "produto", "lote", "unidade_identificada")
