"""URLs do app vendas."""
from django.urls import path

from .views import VendaBalcaoView, VendaCancelarView, VendaConfirmacaoView

app_name = "vendas"

urlpatterns = [
    path("balcao/", VendaBalcaoView.as_view(), name="balcao"),
    path("<int:pk>/confirmacao/", VendaConfirmacaoView.as_view(), name="confirmacao"),
    path("<int:pk>/cancelar/", VendaCancelarView.as_view(), name="cancelar"),
]
