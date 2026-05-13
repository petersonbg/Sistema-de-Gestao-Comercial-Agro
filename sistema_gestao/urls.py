"""URLs principais do projeto sistema_gestao."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core.forms import BootstrapAuthenticationForm
from core.views import dashboard, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=BootstrapAuthenticationForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", logout_view, name="logout"),
    path("clientes/", include("clientes.urls")),
    path("fornecedores/", include("fornecedores.urls")),
    path("produtos/", include("produtos.urls")),
    path("estoque/", include("estoque.urls")),
]
