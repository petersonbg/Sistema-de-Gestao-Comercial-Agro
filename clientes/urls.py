"""URLs do app clientes."""
from django.urls import path

from .views import ClienteCreateView, ClienteDetailView, ClienteInativarView, ClienteListView, ClienteUpdateView

app_name = "clientes"

urlpatterns = [
    path("", ClienteListView.as_view(), name="list"),
    path("novo/", ClienteCreateView.as_view(), name="create"),
    path("<int:pk>/", ClienteDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", ClienteUpdateView.as_view(), name="update"),
    path("<int:pk>/inativar/", ClienteInativarView.as_view(), name="inactivate"),
]
