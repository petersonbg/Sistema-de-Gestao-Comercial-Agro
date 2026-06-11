"""Models do app vendas."""
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Venda(models.Model):
    """Venda comercial finalizada ou cancelada."""

    class FormaPagamento(models.TextChoices):
        DINHEIRO = "dinheiro", "Dinheiro"
        PIX = "pix", "Pix"
        DEBITO = "debito", "Cartão de débito"
        CREDITO = "credito", "Cartão de crédito"

    class Status(models.TextChoices):
        FINALIZADA = "finalizada", "Finalizada"
        CANCELADA = "cancelada", "Cancelada"

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="vendas")
    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.SET_NULL,
        related_name="vendas",
        blank=True,
        null=True,
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="vendas")
    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vendas_canceladas",
        blank=True,
        null=True,
    )
    data = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    forma_pagamento = models.CharField(max_length=20, choices=FormaPagamento.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.FINALIZADA)
    observacoes = models.TextField(blank=True)
    motivo_cancelamento = models.TextField(blank=True)
    cancelado_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data", "-id"]
        verbose_name = "venda"
        verbose_name_plural = "vendas"
        constraints = [
            models.CheckConstraint(check=Q(subtotal__gte=0), name="venda_subtotal_gte_0"),
            models.CheckConstraint(check=Q(desconto__gte=0), name="venda_desconto_gte_0"),
            models.CheckConstraint(check=Q(total__gte=0), name="venda_total_gte_0"),
        ]

    def __str__(self):
        return f"Venda #{self.pk or 'nova'} - {self.data:%d/%m/%Y}"


class VendaItem(models.Model):
    """Item de uma venda."""

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="venda_itens")
    venda = models.ForeignKey("vendas.Venda", on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey("produtos.Produto", on_delete=models.PROTECT, related_name="venda_itens")
    lote = models.ForeignKey(
        "estoque.LoteEstoque",
        on_delete=models.PROTECT,
        related_name="venda_itens",
        blank=True,
        null=True,
    )
    unidade_identificada = models.ForeignKey(
        "estoque.UnidadeIdentificada",
        on_delete=models.PROTECT,
        related_name="venda_itens",
        blank=True,
        null=True,
    )
    quantidade = models.DecimalField(max_digits=12, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    desconto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]
        verbose_name = "item de venda"
        verbose_name_plural = "itens de venda"
        constraints = [
            models.CheckConstraint(check=Q(quantidade__gt=0), name="venda_item_quantidade_gt_0"),
            models.CheckConstraint(check=Q(preco_unitario__gte=0), name="venda_item_preco_unitario_gte_0"),
            models.CheckConstraint(check=Q(desconto__gte=0), name="venda_item_desconto_gte_0"),
            models.CheckConstraint(check=Q(subtotal__gte=0), name="venda_item_subtotal_gte_0"),
        ]

    def __str__(self):
        return f"{self.produto} - {self.quantidade}"
