"""Models do app usuarios."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuário personalizado do sistema."""

    class Perfil(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        VENDEDOR = "vendedor", "Vendedor"

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        related_name="usuarios",
        blank=True,
        null=True,
    )
    perfil = models.CharField(max_length=20, choices=Perfil.choices, default=Perfil.VENDEDOR)
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["first_name", "last_name", "username"]
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self):
        nome = self.get_full_name()
        return nome or self.username
