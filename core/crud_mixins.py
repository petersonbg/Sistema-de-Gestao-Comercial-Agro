"""Mixins reutilizáveis para CRUDs tradicionais por empresa."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from .permissions import AdministradorRequiredMixin, VendedorOuAdministradorRequiredMixin


class EmpresaObrigatoriaBaseMixin(LoginRequiredMixin):
    """Exige usuário autenticado e empresa vinculada."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if not getattr(request.user, "empresa", None):
            messages.error(request, "Seu usuário precisa estar vinculado a uma empresa para acessar este módulo.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_empresa(self):
        """Retorna a empresa do usuário logado."""
        return self.request.user.empresa


class EmpresaObrigatoriaMixin(EmpresaObrigatoriaBaseMixin, VendedorOuAdministradorRequiredMixin):
    """Exige empresa vinculada e perfil de vendedor ou administrador."""


class EmpresaAdministradorObrigatoriaMixin(EmpresaObrigatoriaBaseMixin, AdministradorRequiredMixin):
    """Exige empresa vinculada e perfil de administrador."""
