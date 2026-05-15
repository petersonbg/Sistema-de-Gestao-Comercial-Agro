"""URLs do app estoque."""
from django.urls import path

from .views import EntradaEstoqueView

app_name = "estoque"

urlpatterns = [
    path("entradas/nova/", EntradaEstoqueView.as_view(), name="entrada"),
]
