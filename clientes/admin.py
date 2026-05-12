"""Configuração do Django Admin para clientes."""
from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "empresa", "tipo_pessoa", "cpf_cnpj", "telefone", "whatsapp", "cidade", "ativo")
    search_fields = ("nome", "cpf_cnpj", "telefone", "whatsapp", "email", "empresa__nome_fantasia")
    list_filter = ("empresa", "tipo_pessoa", "ativo", "estado", "cidade")
    readonly_fields = ("criado_em", "atualizado_em")
    fieldsets = (
        ("Identificação", {"fields": ("empresa", "nome", "tipo_pessoa", "cpf_cnpj", "ativo")}),
        ("Contato", {"fields": ("telefone", "whatsapp", "email")}),
        ("Endereço", {"fields": ("endereco", "cidade", "estado", "cep")}),
        ("Observações", {"fields": ("observacoes",)}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )
