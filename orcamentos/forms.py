"""Formulários do módulo de orçamentos."""
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone

from clientes.models import Cliente
from produtos.models import Produto
from vendas.models import Venda

from .models import Orcamento, OrcamentoItem


class OrcamentoFiltroForm(forms.Form):
    """Filtros da listagem de orçamentos."""

    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=[("", "Todos os status")] + list(Orcamento.Status.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    cliente = forms.ModelChoiceField(
        label="Cliente",
        queryset=Cliente.objects.none(),
        required=False,
        empty_label="Todos os clientes",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(empresa=empresa, ativo=True).order_by("nome")


class OrcamentoForm(forms.ModelForm):
    """Formulário de cabeçalho do orçamento."""

    class Meta:
        model = Orcamento
        fields = ("cliente", "validade", "desconto", "observacoes")
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select", "autofocus": True}),
            "validade": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "desconto": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        self.empresa = empresa
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(empresa=empresa, ativo=True).order_by("nome")
        self.fields["desconto"].initial = self.fields["desconto"].initial or Decimal("0.00")

    def clean_validade(self):
        validade = self.cleaned_data["validade"]
        if validade < timezone.localdate():
            raise ValidationError("A validade do orçamento não pode estar no passado.")
        return validade


class OrcamentoItemForm(forms.ModelForm):
    """Formulário de item do orçamento."""

    class Meta:
        model = OrcamentoItem
        fields = ("produto", "quantidade", "desconto")
        widgets = {
            "produto": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "desconto": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        self.empresa = empresa
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.filter(empresa=empresa, ativo=True).order_by("nome")
        self.fields["desconto"].initial = self.fields["desconto"].initial or Decimal("0.00")
        self.fields["quantidade"].initial = self.fields["quantidade"].initial or Decimal("1.000")

    def clean(self):
        cleaned_data = super().clean()
        produto = cleaned_data.get("produto")
        quantidade = cleaned_data.get("quantidade") or Decimal("0")
        desconto = cleaned_data.get("desconto") or Decimal("0")
        if not produto:
            return cleaned_data
        if produto.tipo_controle_estoque == Produto.TipoControleEstoque.SERIAL:
            cleaned_data["quantidade"] = Decimal("1.000")
            quantidade = Decimal("1.000")
        subtotal_bruto = produto.preco_venda * quantidade
        if desconto > subtotal_bruto:
            self.add_error("desconto", "Desconto do item não pode ser maior que o subtotal do item.")
        return cleaned_data


class BaseOrcamentoItemFormSet(BaseInlineFormSet):
    """Valida os itens informados no orçamento."""

    def __init__(self, *args, empresa=None, **kwargs):
        self.empresa = empresa
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empresa = empresa
            form.fields["produto"].queryset = Produto.objects.filter(empresa=empresa, ativo=True).order_by("nome")

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        itens_validos = 0
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            produto = form.cleaned_data.get("produto")
            quantidade = form.cleaned_data.get("quantidade")
            if produto and quantidade:
                itens_validos += 1
        if itens_validos == 0:
            raise ValidationError("Informe ao menos um produto para salvar o orçamento.")


OrcamentoItemFormSet = inlineformset_factory(
    Orcamento,
    OrcamentoItem,
    form=OrcamentoItemForm,
    formset=BaseOrcamentoItemFormSet,
    extra=5,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ConverterOrcamentoForm(forms.Form):
    """Formulário de conversão do orçamento em venda."""

    forma_pagamento = forms.ChoiceField(
        label="Forma de pagamento",
        choices=Venda.FormaPagamento.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
