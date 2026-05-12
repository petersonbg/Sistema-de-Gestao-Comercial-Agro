"""Configuração do Django Admin para usuários."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "empresa", "perfil", "telefone", "ativo", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email", "telefone", "empresa__nome_fantasia")
    list_filter = ("perfil", "ativo", "is_staff", "is_superuser", "is_active", "empresa")
    readonly_fields = ("last_login", "date_joined")
    fieldsets = UserAdmin.fieldsets + (
        ("Dados comerciais", {"fields": ("empresa", "perfil", "telefone", "ativo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Dados comerciais", {"fields": ("empresa", "perfil", "telefone", "ativo")}),
    )
