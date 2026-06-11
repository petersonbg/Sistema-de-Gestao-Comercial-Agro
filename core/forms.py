"""Formulários centrais da aplicação."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class BootstrapAuthenticationForm(AuthenticationForm):
    """Formulário de login com classes Bootstrap."""

    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite seu usuário",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite sua senha",
                "autocomplete": "current-password",
            }
        ),
    )
