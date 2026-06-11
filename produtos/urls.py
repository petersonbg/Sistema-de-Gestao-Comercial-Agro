"""URLs do app produtos."""
from django.urls import path

from .views import (
    CategoriaCreateView,
    CategoriaDetailView,
    CategoriaInativarView,
    CategoriaListView,
    CategoriaUpdateView,
    MarcaCreateView,
    MarcaDetailView,
    MarcaInativarView,
    MarcaListView,
    MarcaUpdateView,
    ProdutoCreateView,
    ProdutoDetailView,
    ProdutoInativarView,
    ProdutoListView,
    ProdutoUpdateView,
)

app_name = "produtos"

urlpatterns = [
    path("categorias/", CategoriaListView.as_view(), name="categoria_list"),
    path("categorias/nova/", CategoriaCreateView.as_view(), name="categoria_create"),
    path("categorias/<int:pk>/", CategoriaDetailView.as_view(), name="categoria_detail"),
    path("categorias/<int:pk>/editar/", CategoriaUpdateView.as_view(), name="categoria_update"),
    path("categorias/<int:pk>/inativar/", CategoriaInativarView.as_view(), name="categoria_inactivate"),
    path("marcas/", MarcaListView.as_view(), name="marca_list"),
    path("marcas/nova/", MarcaCreateView.as_view(), name="marca_create"),
    path("marcas/<int:pk>/", MarcaDetailView.as_view(), name="marca_detail"),
    path("marcas/<int:pk>/editar/", MarcaUpdateView.as_view(), name="marca_update"),
    path("marcas/<int:pk>/inativar/", MarcaInativarView.as_view(), name="marca_inactivate"),
    path("", ProdutoListView.as_view(), name="produto_list"),
    path("novo/", ProdutoCreateView.as_view(), name="produto_create"),
    path("<int:pk>/", ProdutoDetailView.as_view(), name="produto_detail"),
    path("<int:pk>/editar/", ProdutoUpdateView.as_view(), name="produto_update"),
    path("<int:pk>/inativar/", ProdutoInativarView.as_view(), name="produto_inactivate"),
]
