"""Formulários do módulo de estoque."""
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from fornecedores.models import Fornecedor
from produtos.models import Produto

from .models import LoteEstoque, UnidadeIdentificada


class ProdutoEntradaForm(forms.Form):
    """Formulário inicial para seleção do produto da entrada."""

    produto = forms.ModelChoiceField(
        label="Produto",
        queryset=Produto.objects.none(),
        widget=forms.Select(attrs={"class": "form-select", "onchange": "this.form.submit()"}),
        empty_label="Selecione um produto",
    )

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.filter(empresa=empresa, ativo=True).order_by("nome")


class EntradaEstoqueBaseForm(forms.Form):
    """Base para formulários de entrada por empresa."""

    def __init__(self, *args, empresa=None, produto=None, **kwargs):
        self.empresa = empresa
        self.produto = produto
        super().__init__(*args, **kwargs)
        if "fornecedor" in self.fields:
            self.fields["fornecedor"].queryset = Fornecedor.objects.filter(empresa=empresa, ativo=True).order_by("nome")

    def validar_nao_negativo(self, field_name, label):
        """Valida campos decimais que não podem receber valores negativos."""
        valor = self.cleaned_data.get(field_name)
        if valor is not None and valor < Decimal("0"):
            raise ValidationError(f"{label} não pode ser negativo.")
        return valor


class EntradaSimplesForm(EntradaEstoqueBaseForm):
    """Entrada de produto com controle por quantidade simples."""

    fornecedor = forms.ModelChoiceField(
        label="Fornecedor",
        queryset=Fornecedor.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Fornecedor não informado",
    )
    quantidade = forms.DecimalField(
        label="Quantidade",
        max_digits=12,
        decimal_places=3,
        min_value=Decimal("0.001"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
    )
    preco_custo = forms.DecimalField(
        label="Preço de custo",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    observacao = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )


class EntradaLoteForm(EntradaEstoqueBaseForm):
    """Entrada de produto com controle por lote e validade."""

    fornecedor = forms.ModelChoiceField(
        label="Fornecedor",
        queryset=Fornecedor.objects.none(),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Selecione um fornecedor",
    )
    numero_lote = forms.CharField(
        label="Número do lote",
        max_length=80,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    validade = forms.DateField(
        label="Validade",
        required=True,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    quantidade = forms.DecimalField(
        label="Quantidade",
        max_digits=12,
        decimal_places=3,
        min_value=Decimal("0.001"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
    )
    preco_custo = forms.DecimalField(
        label="Preço de custo",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    observacao = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def clean_numero_lote(self):
        numero_lote = self.cleaned_data.get("numero_lote", "").strip()
        if self.empresa and self.produto:
            if LoteEstoque.objects.filter(
                empresa=self.empresa,
                produto=self.produto,
                numero_lote=numero_lote,
            ).exists():
                raise ValidationError("Já existe um lote com este número para este produto nesta empresa.")
        return numero_lote


class EntradaSerialForm(EntradaEstoqueBaseForm):
    """Entrada de produto com controle por unidade identificada."""

    fornecedor = forms.ModelChoiceField(
        label="Fornecedor",
        queryset=Fornecedor.objects.none(),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Selecione um fornecedor",
    )
    numero_serie = forms.CharField(
        label="Número de série",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    chassi = forms.CharField(
        label="Chassi",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    modelo = forms.CharField(
        label="Modelo",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cor = forms.CharField(
        label="Cor",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    ano_modelo = forms.IntegerField(
        label="Ano/modelo",
        required=False,
        min_value=1900,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    preco_custo = forms.DecimalField(
        label="Preço de custo",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    preco_venda = forms.DecimalField(
        label="Preço de venda",
        max_digits=12,
        decimal_places=2,
        required=False,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    observacoes = forms.CharField(
        label="Observações da unidade",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    observacao_movimentacao = forms.CharField(
        label="Observação da movimentação",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def clean(self):
        cleaned_data = super().clean()
        numero_serie = (cleaned_data.get("numero_serie") or "").strip()
        chassi = (cleaned_data.get("chassi") or "").strip()

        if not numero_serie and not chassi:
            raise ValidationError("Informe pelo menos o número de série ou o chassi.")

        duplicados = UnidadeIdentificada.objects.filter(empresa=self.empresa)
        if numero_serie and duplicados.filter(numero_serie=numero_serie).exists():
            self.add_error("numero_serie", "Já existe uma unidade com este número de série nesta empresa.")
        if chassi and duplicados.filter(chassi=chassi).exists():
            self.add_error("chassi", "Já existe uma unidade com este chassi nesta empresa.")

        return cleaned_data
