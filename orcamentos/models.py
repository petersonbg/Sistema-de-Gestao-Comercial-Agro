"""Models do app orcamentos."""
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Orcamento(models.Model):
    """Orçamento comercial emitido para um cliente."""

    class Status(models.TextChoices):
        ABERTO = "aberto", "Aberto"
        APROVADO = "aprovado", "Aprovado"
        CONVERTIDO = "convertido", "Convertido"
        CANCELADO = "cancelado", "Cancelado"
        VENCIDO = "vencido", "Vencido"

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="orcamentos")
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="orcamentos")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orcamentos")
    data = models.DateTimeField(default=timezone.now)
    validade = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ABERTO)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data", "-id"]
        verbose_name = "orçamento"
        verbose_name_plural = "orçamentos"
        constraints = [
            models.CheckConstraint(check=Q(subtotal__gte=0), name="orcamento_subtotal_gte_0"),
            models.CheckConstraint(check=Q(desconto__gte=0), name="orcamento_desconto_gte_0"),
            models.CheckConstraint(check=Q(total__gte=0), name="orcamento_total_gte_0"),
        ]

    def __str__(self):
        return f"Orçamento #{self.pk or 'novo'} - {self.cliente}"


class OrcamentoItem(models.Model):
    """Item de um orçamento."""

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="orcamento_itens")
    orcamento = models.ForeignKey("orcamentos.Orcamento", on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey("produtos.Produto", on_delete=models.PROTECT, related_name="orcamento_itens")
    quantidade = models.DecimalField(max_digits=12, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    desconto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]
        verbose_name = "item de orçamento"
        verbose_name_plural = "itens de orçamento"
        constraints = [
            models.CheckConstraint(check=Q(quantidade__gt=0), name="orcamento_item_quantidade_gt_0"),
            models.CheckConstraint(check=Q(preco_unitario__gte=0), name="orcamento_item_preco_unitario_gte_0"),
            models.CheckConstraint(check=Q(desconto__gte=0), name="orcamento_item_desconto_gte_0"),
            models.CheckConstraint(check=Q(subtotal__gte=0), name="orcamento_item_subtotal_gte_0"),
        ]

    def __str__(self):
        return f"{self.produto} - {self.quantidade}"
