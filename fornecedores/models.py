"""Models do app fornecedores."""
from django.db import models
from django.db.models import Q


class Fornecedor(models.Model):
    """Cadastro de fornecedores da empresa."""

    class TipoPessoa(models.TextChoices):
        FISICA = "fisica", "Física"
        JURIDICA = "juridica", "Jurídica"

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="fornecedores")
    nome = models.CharField(max_length=150)
    tipo_pessoa = models.CharField(max_length=10, choices=TipoPessoa.choices, default=TipoPessoa.JURIDICA)
    cpf_cnpj = models.CharField(max_length=18, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    cep = models.CharField(max_length=10, blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "fornecedor"
        verbose_name_plural = "fornecedores"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "cpf_cnpj"],
                condition=~Q(cpf_cnpj=""),
                name="uniq_fornecedor_cpf_cnpj_por_empresa",
            )
        ]

    def __str__(self):
        return self.nome
