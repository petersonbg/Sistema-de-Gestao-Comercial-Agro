"""Permissões simples por perfil de usuário para views tradicionais."""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


PERFIL_ADMINISTRADOR = "administrador"
PERFIL_VENDEDOR = "vendedor"


def usuario_tem_perfil(user, perfis):
    """Verifica se o usuário autenticado possui um dos perfis informados."""
    return user.is_authenticated and (user.is_superuser or getattr(user, "perfil", None) in perfis)


def perfil_required(*perfis):
    """Decorator para restringir uma view a um ou mais perfis."""

    def check(user):
        if usuario_tem_perfil(user, perfis):
            return True
        if user.is_authenticated:
            raise PermissionDenied
        return False

    return user_passes_test(check)


def administrador_required(view_func):
    """Atalho para views acessíveis apenas por administradores."""
    return perfil_required(PERFIL_ADMINISTRADOR)(view_func)


def vendedor_ou_administrador_required(view_func):
    """Atalho para views comerciais acessíveis por vendedores e administradores."""
    return perfil_required(PERFIL_ADMINISTRADOR, PERFIL_VENDEDOR)(view_func)


class PerfilRequiredMixin(UserPassesTestMixin):
    """Mixin simples para restringir class-based views por perfil."""

    perfis_permitidos = ()
    raise_exception = True

    def test_func(self):
        return usuario_tem_perfil(self.request.user, self.perfis_permitidos)


class AdministradorRequiredMixin(PerfilRequiredMixin):
    """Mixin para views acessíveis apenas por administradores."""

    perfis_permitidos = (PERFIL_ADMINISTRADOR,)


class VendedorOuAdministradorRequiredMixin(PerfilRequiredMixin):
    """Mixin para views comerciais acessíveis por vendedores e administradores."""

    perfis_permitidos = (PERFIL_ADMINISTRADOR, PERFIL_VENDEDOR)
