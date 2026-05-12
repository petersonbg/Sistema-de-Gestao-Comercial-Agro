"""Models do app estoque."""
from django.conf import settings
from django.db import models
from django.db.models import Q


class LoteEstoque(models.Model):
    """Controle de estoque por lote e validade."""

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="lotes_estoque")
    produto = models.ForeignKey("produtos.Produto", on_delete=models.PROTECT, related_name="lotes_estoque")
    fornecedor = models.ForeignKey("fornecedores.Fornecedor", on_delete=models.PROTECT, related_name="lotes_estoque")
    numero_lote = models.CharField(max_length=80)
    validade = models.DateField()
    quantidade_inicial = models.DecimalField(max_digits=12, decimal_places=3)
    quantidade_atual = models.DecimalField(max_digits=12, decimal_places=3)
    preco_custo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    data_entrada = models.DateField()
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["validade", "numero_lote"]
        verbose_name = "lote de estoque"
        verbose_name_plural = "lotes de estoque"
        constraints = [
            models.UniqueConstraint(fields=["empresa", "produto", "numero_lote"], name="uniq_lote_produto_por_empresa"),
            models.CheckConstraint(check=Q(quantidade_inicial__gte=0), name="lote_quantidade_inicial_gte_0"),
            models.CheckConstraint(check=Q(quantidade_atual__gte=0), name="lote_quantidade_atual_gte_0"),
            models.CheckConstraint(check=Q(preco_custo__gte=0), name="lote_preco_custo_gte_0"),
        ]

    def __str__(self):
        return f"{self.produto} - Lote {self.numero_lote}"


class UnidadeIdentificada(models.Model):
    """Controle de triciclos, máquinas ou veículos por identificação individual."""

    class Status(models.TextChoices):
        DISPONIVEL = "disponivel", "Disponível"
        RESERVADO = "reservado", "Reservado"
        VENDIDO = "vendido", "Vendido"
        INATIVO = "inativo", "Inativo"

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="unidades_identificadas")
    produto = models.ForeignKey("produtos.Produto", on_delete=models.PROTECT, related_name="unidades_identificadas")
    fornecedor = models.ForeignKey(
        "fornecedores.Fornecedor",
        on_delete=models.PROTECT,
        related_name="unidades_identificadas",
        blank=True,
        null=True,
    )
    numero_serie = models.CharField(max_length=100, blank=True)
    chassi = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    cor = models.CharField(max_length=50, blank=True)
    ano_modelo = models.PositiveIntegerField(blank=True, null=True)
    preco_custo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    preco_venda = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISPONIVEL)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["produto__nome", "numero_serie", "chassi"]
        verbose_name = "unidade identificada"
        verbose_name_plural = "unidades identificadas"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "numero_serie"],
                condition=~Q(numero_serie=""),
                name="uniq_unidade_numero_serie_por_empresa",
            ),
            models.UniqueConstraint(
                fields=["empresa", "chassi"],
                condition=~Q(chassi=""),
                name="uniq_unidade_chassi_por_empresa",
            ),
            models.CheckConstraint(check=Q(preco_custo__gte=0), name="unidade_preco_custo_gte_0"),
            models.CheckConstraint(check=Q(preco_venda__gte=0), name="unidade_preco_venda_gte_0"),
        ]

    def __str__(self):
        identificacao = self.chassi or self.numero_serie or self.modelo or self.pk
        return f"{self.produto} - {identificacao}"


class MovimentacaoEstoque(models.Model):
    """Histórico de entradas, saídas e ajustes de estoque."""

    class TipoMovimentacao(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SAIDA = "saida", "Saída"
        AJUSTE = "ajuste", "Ajuste"
        CANCELAMENTO_VENDA = "cancelamento_venda", "Cancelamento de venda"

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="movimentacoes_estoque")
    produto = models.ForeignKey("produtos.Produto", on_delete=models.PROTECT, related_name="movimentacoes_estoque")
    tipo_movimentacao = models.CharField(max_length=20, choices=TipoMovimentacao.choices)
    quantidade = models.DecimalField(max_digits=12, decimal_places=3)
    lote = models.ForeignKey(
        "estoque.LoteEstoque",
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        blank=True,
        null=True,
    )
    unidade_identificada = models.ForeignKey(
        "estoque.UnidadeIdentificada",
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        blank=True,
        null=True,
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="movimentacoes_estoque")
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "movimentação de estoque"
        verbose_name_plural = "movimentações de estoque"
        constraints = [
            models.CheckConstraint(check=Q(quantidade__gt=0), name="movimentacao_quantidade_gt_0")
        ]

    def __str__(self):
        return f"{self.get_tipo_movimentacao_display()} - {self.produto} ({self.quantidade})"
