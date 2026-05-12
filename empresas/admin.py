"""Configuração do Django Admin para empresas."""
from django.contrib import admin

from core.admin_permissions import AdminSomenteAdministradorMixin

from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(AdminSomenteAdministradorMixin, admin.ModelAdmin):
    list_display = ("nome_fantasia", "razao_social", "cnpj", "telefone", "cidade", "estado", "ativo")
    search_fields = ("nome_fantasia", "razao_social", "cnpj", "email", "telefone")
    list_filter = ("ativo", "estado", "cidade")
    readonly_fields = ("criado_em", "atualizado_em")
    fieldsets = (
        ("Identificação", {"fields": ("nome_fantasia", "razao_social", "cnpj", "logo", "ativo")}),
        ("Contato", {"fields": ("telefone", "email")}),
        ("Endereço", {"fields": ("endereco", "cidade", "estado", "cep")}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )
