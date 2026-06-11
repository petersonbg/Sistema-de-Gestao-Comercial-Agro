"""Formulários do app fornecedores."""
from django import forms
from django.core.exceptions import ValidationError

from .models import Fornecedor


class FornecedorForm(forms.ModelForm):
    """Formulário de cadastro e edição de fornecedores."""

    class Meta:
        model = Fornecedor
        fields = (
            "nome",
            "tipo_pessoa",
            "cpf_cnpj",
            "telefone",
            "email",
            "endereco",
            "cidade",
            "estado",
            "cep",
            "observacoes",
        )
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
            "tipo_pessoa": forms.Select(attrs={"class": "form-select"}),
            "cpf_cnpj": forms.TextInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "endereco": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.TextInput(attrs={"class": "form-control", "maxlength": 2}),
            "cep": forms.TextInput(attrs={"class": "form-control"}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        self.empresa = empresa
        super().__init__(*args, **kwargs)

    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get("cpf_cnpj", "").strip()
        if not cpf_cnpj or not self.empresa:
            return cpf_cnpj

        queryset = Fornecedor.objects.filter(empresa=self.empresa, cpf_cnpj=cpf_cnpj)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Já existe um fornecedor com este CPF/CNPJ nesta empresa.")
        return cpf_cnpj
