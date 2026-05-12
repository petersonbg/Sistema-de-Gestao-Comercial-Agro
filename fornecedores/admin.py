"""Configuração do Django Admin para fornecedores."""
from django.contrib import admin

from core.admin_permissions import AdminSomenteAdministradorMixin

from .models import Fornecedor


@admin.register(Fornecedor)
class FornecedorAdmin(AdminSomenteAdministradorMixin, admin.ModelAdmin):
    list_display = ("nome", "empresa", "tipo_pessoa", "cpf_cnpj", "telefone", "email", "cidade", "ativo")
    search_fields = ("nome", "cpf_cnpj", "telefone", "email", "empresa__nome_fantasia")
    list_filter = ("empresa", "tipo_pessoa", "ativo", "estado", "cidade")
    readonly_fields = ("criado_em", "atualizado_em")
    fieldsets = (
        ("Identificação", {"fields": ("empresa", "nome", "tipo_pessoa", "cpf_cnpj", "ativo")}),
        ("Contato", {"fields": ("telefone", "email")}),
        ("Endereço", {"fields": ("endereco", "cidade", "estado", "cep")}),
        ("Observações", {"fields": ("observacoes",)}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )
