"""Formulários do módulo de vendas."""
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from clientes.models import Cliente
from estoque.models import UnidadeIdentificada
from produtos.models import Produto

from .models import Venda


class ProdutoBuscaForm(forms.Form):
    """Formulário de busca de produtos para venda balcão."""

    q = forms.CharField(
        label="Buscar produto",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nome, código interno ou código de barras",
                "autofocus": True,
            }
        ),
    )


class AdicionarItemVendaForm(forms.Form):
    """Formulário para adicionar um produto ao carrinho da venda."""

    produto_id = forms.IntegerField(widget=forms.HiddenInput)
    unidade_identificada = forms.ModelChoiceField(
        label="Unidade",
        queryset=UnidadeIdentificada.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
        empty_label="Selecione a unidade",
    )
    quantidade = forms.DecimalField(
        label="Quantidade",
        max_digits=12,
        decimal_places=3,
        min_value=Decimal("0.001"),
        initial=Decimal("1.000"),
        widget=forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.001"}),
    )
    desconto = forms.DecimalField(
        label="Desconto item",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        initial=Decimal("0.00"),
        widget=forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01"}),
    )

    def __init__(self, *args, empresa=None, produto=None, **kwargs):
        self.empresa = empresa
        self.produto = produto
        super().__init__(*args, **kwargs)
        if produto:
            self.fields["produto_id"].initial = produto.pk
            self.fields["unidade_identificada"].queryset = UnidadeIdentificada.objects.filter(
                empresa=empresa,
                produto=produto,
                status=UnidadeIdentificada.Status.DISPONIVEL,
            ).order_by("chassi", "numero_serie")
            if produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
                self.fields["quantidade"].initial = Decimal("1.000")
                self.fields["quantidade"].widget.attrs["readonly"] = True
                self.fields["unidade_identificada"].required = True
            else:
                self.fields["unidade_identificada"].widget = forms.HiddenInput()

    def clean_produto_id(self):
        produto_id = self.cleaned_data["produto_id"]
        if self.produto and produto_id != self.produto.pk:
            raise ValidationError("Produto inválido para este formulário.")
        return produto_id

    def clean_quantidade(self):
        quantidade = self.cleaned_data["quantidade"]
        if self.produto and self.produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
            return Decimal("1.000")
        return quantidade

    def clean(self):
        cleaned_data = super().clean()
        if not self.produto:
            return cleaned_data

        quantidade = cleaned_data.get("quantidade") or Decimal("0")
        desconto = cleaned_data.get("desconto") or Decimal("0")
        subtotal_bruto = self.produto.preco_venda * quantidade
        if desconto > subtotal_bruto:
            self.add_error("desconto", "Desconto do item não pode ser maior que o subtotal do item.")
        return cleaned_data


class FinalizarVendaForm(forms.Form):
    """Formulário de fechamento da venda balcão."""

    cliente = forms.ModelChoiceField(
        label="Cliente",
        queryset=Cliente.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Consumidor Final",
    )
    forma_pagamento = forms.ChoiceField(
        label="Forma de pagamento",
        choices=Venda.FormaPagamento.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    desconto = forms.DecimalField(
        label="Desconto total",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
        initial=Decimal("0.00"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    observacoes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(empresa=empresa, ativo=True).order_by("nome")


class CancelarVendaForm(forms.Form):
    """Formulário para cancelamento total da venda."""

    motivo = forms.CharField(
        label="Motivo do cancelamento",
        min_length=5,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Informe o motivo do cancelamento",
            }
        ),
    )
