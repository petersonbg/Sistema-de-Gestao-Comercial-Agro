"""Models do app produtos."""
from django.db import models
from django.db.models import Q


class Categoria(models.Model):
    """Categoria de produtos por empresa."""

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="categorias")
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        constraints = [
            models.UniqueConstraint(fields=["empresa", "nome"], name="uniq_categoria_nome_por_empresa")
        ]

    def __str__(self):
        return self.nome


class Marca(models.Model):
    """Marca de produtos por empresa."""

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="marcas")
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "marca"
        verbose_name_plural = "marcas"
        constraints = [
            models.UniqueConstraint(fields=["empresa", "nome"], name="uniq_marca_nome_por_empresa")
        ]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """Cadastro único de produtos com diferentes tipos de controle de estoque."""

    class TipoProduto(models.TextChoices):
        ADUBO = "adubo", "Adubo/Fertilizante"
        PECA_MECANICA = "peca_mecanica", "Peça mecânica"
        TRICICLO = "triciclo", "Triciclo agrícola"
        FERRAMENTA = "ferramenta", "Ferramenta"
        ACESSORIO = "acessorio", "Acessório"
        OLEO_LUBRIFICANTE = "oleo_lubrificante", "Óleo lubrificante"
        OUTRO = "outro", "Outro"

    class TipoControleEstoque(models.TextChoices):
        SIMPLES = "simples", "Quantidade simples"
        LOTE = "lote", "Lote e validade"
        SERIAL = "serial", "Unidade identificada"

    class UnidadeVenda(models.TextChoices):
        UNIDADE = "unidade", "Unidade"
        SACO = "saco", "Saco"
        GALAO = "galao", "Galão"
        BOMBONA = "bombona", "Bombona"
        CAIXA = "caixa", "Caixa"
        LITRO_FECHADO = "litro_fechado", "Litro fechado"
        KG_FECHADO = "kg_fechado", "Kg fechado"

    class UnidadeReferencia(models.TextChoices):
        KG = "kg", "Kg"
        LITRO = "litro", "Litro"
        UNIDADE = "unidade", "Unidade"

    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE, related_name="produtos")
    categoria = models.ForeignKey("produtos.Categoria", on_delete=models.PROTECT, related_name="produtos")
    marca = models.ForeignKey(
        "produtos.Marca",
        on_delete=models.PROTECT,
        related_name="produtos",
        blank=True,
        null=True,
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    codigo_interno = models.CharField(max_length=50)
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)
    codigo_bndes = models.CharField(max_length=50, blank=True)
    codigo_mda = models.CharField(max_length=50, blank=True)
    ncm = models.CharField(max_length=10, blank=True)
    tipo_produto = models.CharField(max_length=30, choices=TipoProduto.choices, default=TipoProduto.OUTRO)
    tipo_controle_estoque = models.CharField(
        max_length=10,
        choices=TipoControleEstoque.choices,
        default=TipoControleEstoque.SIMPLES,
    )
    unidade_venda = models.CharField(max_length=20, choices=UnidadeVenda.choices, default=UnidadeVenda.UNIDADE)
    quantidade_por_embalagem = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    unidade_referencia = models.CharField(
        max_length=10,
        choices=UnidadeReferencia.choices,
        blank=True,
        null=True,
    )
    preco_custo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    preco_venda = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estoque_atual = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    estoque_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        constraints = [
            models.UniqueConstraint(fields=["empresa", "codigo_interno"], name="uniq_produto_codigo_interno_por_empresa"),
            models.UniqueConstraint(
                fields=["empresa", "codigo_barras"],
                condition=Q(codigo_barras__isnull=False) & ~Q(codigo_barras=""),
                name="uniq_produto_codigo_barras_por_empresa",
            ),
            models.CheckConstraint(check=Q(preco_custo__gte=0), name="produto_preco_custo_gte_0"),
            models.CheckConstraint(check=Q(preco_venda__gte=0), name="produto_preco_venda_gte_0"),
            models.CheckConstraint(check=Q(estoque_atual__gte=0), name="produto_estoque_atual_gte_0"),
            models.CheckConstraint(check=Q(estoque_minimo__gte=0), name="produto_estoque_minimo_gte_0"),
        ]

    def __str__(self):
        return f"{self.codigo_interno} - {self.nome}"
