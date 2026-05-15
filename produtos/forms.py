"""Formulários do app produtos."""
from decimal import Decimal

from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError

from .models import Categoria, Marca, Produto


class CategoriaForm(forms.ModelForm):
    """Formulário de cadastro e edição de categorias."""

    class Meta:
        model = Categoria
        fields = ("nome", "descricao")
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        self.empresa = empresa
        super().__init__(*args, **kwargs)

    def clean_nome(self):
        nome = self.cleaned_data.get("nome", "").strip()
        queryset = Categoria.objects.filter(empresa=self.empresa, nome__iexact=nome)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if self.empresa and queryset.exists():
            raise ValidationError("Já existe uma categoria com este nome nesta empresa.")
        return nome


class MarcaForm(forms.ModelForm):
    """Formulário de cadastro e edição de marcas."""

    class Meta:
        model = Marca
        fields = ("nome",)
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        self.empresa = empresa
        super().__init__(*args, **kwargs)

    def clean_nome(self):
        nome = self.cleaned_data.get("nome", "").strip()
        queryset = Marca.objects.filter(empresa=self.empresa, nome__iexact=nome)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if self.empresa and queryset.exists():
            raise ValidationError("Já existe uma marca com este nome nesta empresa.")
        return nome


class ProdutoForm(forms.ModelForm):
    """Formulário de cadastro e edição de produtos."""

    class Meta:
        model = Produto
        fields = (
            "categoria",
            "marca",
            "nome",
            "descricao",
            "codigo_barras",
            "chassi",
            "codigo_bndes",
            "codigo_mda",
            "ncm",
            "tipo_produto",
            "tipo_controle_estoque",
            "unidade_venda",
            "quantidade_por_embalagem",
            "unidade_referencia",
            "preco_custo",
            "preco_venda",
            "estoque_atual",
            "estoque_minimo",
        )
        widgets = {
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "marca": forms.Select(attrs={"class": "form-select"}),
            "nome": forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "codigo_barras": forms.TextInput(attrs={"class": "form-control"}),
            "chassi": forms.TextInput(attrs={"class": "form-control"}),
            "codigo_bndes": forms.TextInput(attrs={"class": "form-control"}),
            "codigo_mda": forms.TextInput(attrs={"class": "form-control"}),
            "ncm": forms.TextInput(attrs={"class": "form-control", "maxlength": 10}),
            "tipo_produto": forms.Select(attrs={"class": "form-select"}),
            "tipo_controle_estoque": forms.Select(attrs={"class": "form-select"}),
            "unidade_venda": forms.Select(attrs={"class": "form-select"}),
            "quantidade_por_embalagem": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "unidade_referencia": forms.Select(attrs={"class": "form-select"}),
            "preco_custo": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "preco_venda": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "estoque_atual": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "estoque_minimo": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        self.empresa = empresa
        super().__init__(*args, **kwargs)
        categorias = Categoria.objects.filter(empresa=empresa)
        marcas = Marca.objects.filter(empresa=empresa)
        if self.instance.pk:
            categorias = categorias.filter(Q(ativo=True) | Q(pk=self.instance.categoria_id))
            marcas = marcas.filter(Q(ativo=True) | Q(pk=self.instance.marca_id))
        else:
            categorias = categorias.filter(ativo=True)
            marcas = marcas.filter(ativo=True)

        self.fields["categoria"].queryset = categorias
        self.fields["marca"].queryset = marcas
        self.fields["marca"].required = False
        self.fields["unidade_referencia"].required = False
        self.fields["quantidade_por_embalagem"].required = False

    def clean_codigo_barras(self):
        codigo_barras = (self.cleaned_data.get("codigo_barras") or "").strip()
        if not codigo_barras:
            return ""

        queryset = Produto.objects.filter(empresa=self.empresa, codigo_barras=codigo_barras)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if self.empresa and queryset.exists():
            raise ValidationError("Já existe um produto com este código de barras nesta empresa.")
        return codigo_barras

    def clean_chassi(self):
        chassi = (self.cleaned_data.get("chassi") or "").strip().upper()
        if not chassi:
            return ""

        queryset = Produto.objects.filter(empresa=self.empresa, chassi=chassi)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if self.empresa and queryset.exists():
            raise ValidationError("Já existe um produto com este chassi nesta empresa.")
        return chassi

    def clean_codigo_bndes(self):
        return (self.cleaned_data.get("codigo_bndes") or "").strip()

    def clean_codigo_mda(self):
        return (self.cleaned_data.get("codigo_mda") or "").strip()

    def clean_ncm(self):
        return (self.cleaned_data.get("ncm") or "").strip()

    def clean_preco_custo(self):
        return self._validar_nao_negativo("preco_custo", "Preço de custo")

    def clean_preco_venda(self):
        return self._validar_nao_negativo("preco_venda", "Preço de venda")

    def clean_estoque_minimo(self):
        return self._validar_nao_negativo("estoque_minimo", "Estoque mínimo")

    def clean_estoque_atual(self):
        return self._validar_nao_negativo("estoque_atual", "Estoque atual")

    def _validar_nao_negativo(self, field_name, label):
        valor = self.cleaned_data.get(field_name)
        if valor is not None and valor < Decimal("0"):
            raise ValidationError(f"{label} não pode ser negativo.")
        return valor
