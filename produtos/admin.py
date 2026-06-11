"""Configuração do Django Admin para produtos."""
from django.contrib import admin

from core.admin_permissions import AdminCategoriaProdutoMixin, AdminComercialMixin

from .models import CategoriaProduto, Marca, Produto


@admin.register(CategoriaProduto)
class CategoriaProdutoAdmin(AdminCategoriaProdutoMixin, admin.ModelAdmin):
    list_display = ("nome", "tipo", "empresa", "ativo", "atualizado_em")
    search_fields = ("nome", "descricao", "empresa__nome_fantasia")
    list_filter = ("empresa", "tipo", "ativo")
    readonly_fields = ("criado_em", "atualizado_em")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(empresa=request.user.empresa)


@admin.register(Marca)
class MarcaAdmin(AdminComercialMixin, admin.ModelAdmin):
    list_display = ("nome", "empresa", "ativo")
    search_fields = ("nome", "empresa__nome_fantasia")
    list_filter = ("empresa", "ativo")


@admin.register(Produto)
class ProdutoAdmin(AdminComercialMixin, admin.ModelAdmin):
    list_display = (
        "codigo_interno",
        "nome",
        "chassi",
        "empresa",
        "categoria",
        "marca",
        "tipo_produto",
        "tipo_controle_estoque",
        "unidade_venda",
        "estoque_atual",
        "preco_venda",
        "ativo",
    )
    search_fields = (
        "nome",
        "descricao",
        "codigo_interno",
        "codigo_barras",
        "chassi",
        "codigo_bndes",
        "codigo_mda",
        "ncm",
        "empresa__nome_fantasia",
        "categoria__nome",
        "marca__nome",
    )
    list_filter = ("empresa", "categoria", "tipo_produto", "tipo_controle_estoque", "ativo")
    readonly_fields = ("codigo_interno", "criado_em", "atualizado_em")
    list_select_related = ("empresa", "categoria", "marca")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "categoria":
            kwargs["queryset"] = CategoriaProduto.objects.filter(ativo=True)
            if not request.user.is_superuser:
                kwargs["queryset"] = kwargs["queryset"].filter(empresa=request.user.empresa)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    fieldsets = (
        ("Identificação", {"fields": ("empresa", "categoria", "marca", "nome", "descricao", "ativo")}),
        ("Códigos", {"fields": ("codigo_interno", "codigo_barras", "chassi", "codigo_bndes", "codigo_mda", "ncm")}),
        ("Classificação e controle", {"fields": ("tipo_produto", "tipo_controle_estoque")}),
        (
            "Venda e embalagem",
            {"fields": ("unidade_venda", "quantidade_por_embalagem", "unidade_referencia")},
        ),
        ("Preços", {"fields": ("preco_custo", "preco_venda")}),
        ("Estoque", {"fields": ("estoque_atual", "estoque_minimo")}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )
