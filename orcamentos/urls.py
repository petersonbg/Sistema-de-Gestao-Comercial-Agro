"""URLs do app orcamentos."""
from django.urls import path

from .views import (
    OrcamentoCancelarView,
    OrcamentoConverterView,
    OrcamentoCreateView,
    OrcamentoDetailView,
    OrcamentoListView,
    OrcamentoPdfView,
)

app_name = "orcamentos"

urlpatterns = [
    path("", OrcamentoListView.as_view(), name="list"),
    path("novo/", OrcamentoCreateView.as_view(), name="create"),
    path("<int:pk>/", OrcamentoDetailView.as_view(), name="detail"),
    path("<int:pk>/pdf/", OrcamentoPdfView.as_view(), name="pdf"),
    path("<int:pk>/converter/", OrcamentoConverterView.as_view(), name="convert"),
    path("<int:pk>/cancelar/", OrcamentoCancelarView.as_view(), name="cancel"),
]
