"""Formulários de filtros dos relatórios."""
from django import forms
from django.utils import timezone


class PeriodoForm(forms.Form):
    """Filtro simples por período."""

    data_inicial = forms.DateField(
        label="Data inicial",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    data_final = forms.DateField(
        label="Data final",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    def __init__(self, *args, default_days=30, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            hoje = timezone.localdate()
            self.fields["data_final"].initial = hoje
            self.fields["data_inicial"].initial = hoje - timezone.timedelta(days=default_days)

    def clean(self):
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get("data_inicial")
        data_final = cleaned_data.get("data_final")
        if data_inicial and data_final and data_inicial > data_final:
            raise forms.ValidationError("Data inicial não pode ser maior que a data final.")
        return cleaned_data

    def periodo(self):
        """Retorna as datas limpas ou padrão para consultas."""
        hoje = timezone.localdate()
        data_inicial = self.cleaned_data.get("data_inicial") or hoje - timezone.timedelta(days=30)
        data_final = self.cleaned_data.get("data_final") or hoje
        return data_inicial, data_final
