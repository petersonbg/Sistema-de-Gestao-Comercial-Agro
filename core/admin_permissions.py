"""Permissões reutilizáveis para o Django Admin."""
from .permissions import PERFIL_ADMINISTRADOR, PERFIL_VENDEDOR


class AdminPerfilMixin:
    """Base para liberar ModelAdmin conforme o perfil do usuário."""

    perfis_permitidos = ()

    def usuario_permitido(self, request):
        user = request.user
        return user.is_superuser or getattr(user, "perfil", None) in self.perfis_permitidos

    def has_module_permission(self, request):
        return self.usuario_permitido(request)

    def has_view_permission(self, request, obj=None):
        return self.usuario_permitido(request)

    def has_add_permission(self, request):
        return self.usuario_permitido(request)

    def has_change_permission(self, request, obj=None):
        return self.usuario_permitido(request)

    def has_delete_permission(self, request, obj=None):
        return self.usuario_permitido(request)


class AdminSomenteAdministradorMixin(AdminPerfilMixin):
    """Permite acesso no admin apenas a administradores e superusuários."""

    perfis_permitidos = (PERFIL_ADMINISTRADOR,)


class AdminComercialMixin(AdminPerfilMixin):
    """Permite acesso comercial no admin a administradores, vendedores e superusuários."""

    perfis_permitidos = (PERFIL_ADMINISTRADOR, PERFIL_VENDEDOR)
