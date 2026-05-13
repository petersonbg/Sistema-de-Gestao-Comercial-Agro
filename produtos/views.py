"""Views do CRUD de categorias, marcas e produtos."""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.crud_mixins import EmpresaObrigatoriaMixin

from .forms import CategoriaForm, MarcaForm, ProdutoForm
from .models import Categoria, Marca, Produto


class CategoriaQuerysetMixin(EmpresaObrigatoriaMixin):
    """Restringe categorias à empresa do usuário logado."""

    model = Categoria

    def get_queryset(self):
        return Categoria.objects.filter(empresa=self.get_empresa())


class CategoriaListView(CategoriaQuerysetMixin, ListView):
    """Lista categorias com busca e paginação."""

    template_name = "produtos/categoria_list.html"
    context_object_name = "categorias"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()

        if busca:
            queryset = queryset.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
        if status == "ativo":
            queryset = queryset.filter(ativo=True)
        elif status == "inativo":
            queryset = queryset.filter(ativo=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["busca"] = self.request.GET.get("q", "")
        context["status"] = self.request.GET.get("status", "")
        return context


class CategoriaDetailView(CategoriaQuerysetMixin, DetailView):
    """Exibe detalhes da categoria."""

    template_name = "produtos/categoria_detail.html"
    context_object_name = "categoria"


class CategoriaCreateView(CategoriaQuerysetMixin, CreateView):
    """Cadastra categorias na empresa do usuário logado."""

    form_class = CategoriaForm
    template_name = "produtos/categoria_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, "Categoria cadastrada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível salvar a categoria. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("produtos:categoria_detail", kwargs={"pk": self.object.pk})


class CategoriaUpdateView(CategoriaQuerysetMixin, UpdateView):
    """Edita categorias da empresa do usuário logado."""

    form_class = CategoriaForm
    template_name = "produtos/categoria_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Categoria atualizada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível atualizar a categoria. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("produtos:categoria_detail", kwargs={"pk": self.object.pk})


class CategoriaInativarView(CategoriaQuerysetMixin, View):
    """Inativa categorias em vez de removê-las definitivamente."""

    def post(self, request, *args, **kwargs):
        categoria = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        if not categoria.ativo:
            messages.info(request, "Categoria já estava inativa.")
        else:
            categoria.ativo = False
            categoria.save(update_fields=["ativo"])
            messages.success(request, "Categoria inativada com sucesso.")
        return redirect("produtos:categoria_detail", pk=categoria.pk)


class MarcaQuerysetMixin(EmpresaObrigatoriaMixin):
    """Restringe marcas à empresa do usuário logado."""

    model = Marca

    def get_queryset(self):
        return Marca.objects.filter(empresa=self.get_empresa())


class MarcaListView(MarcaQuerysetMixin, ListView):
    """Lista marcas com busca e paginação."""

    template_name = "produtos/marca_list.html"
    context_object_name = "marcas"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()

        if busca:
            queryset = queryset.filter(nome__icontains=busca)
        if status == "ativo":
            queryset = queryset.filter(ativo=True)
        elif status == "inativo":
            queryset = queryset.filter(ativo=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["busca"] = self.request.GET.get("q", "")
        context["status"] = self.request.GET.get("status", "")
        return context


class MarcaDetailView(MarcaQuerysetMixin, DetailView):
    """Exibe detalhes da marca."""

    template_name = "produtos/marca_detail.html"
    context_object_name = "marca"


class MarcaCreateView(MarcaQuerysetMixin, CreateView):
    """Cadastra marcas na empresa do usuário logado."""

    form_class = MarcaForm
    template_name = "produtos/marca_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, "Marca cadastrada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível salvar a marca. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("produtos:marca_detail", kwargs={"pk": self.object.pk})


class MarcaUpdateView(MarcaQuerysetMixin, UpdateView):
    """Edita marcas da empresa do usuário logado."""

    form_class = MarcaForm
    template_name = "produtos/marca_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Marca atualizada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível atualizar a marca. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("produtos:marca_detail", kwargs={"pk": self.object.pk})


class MarcaInativarView(MarcaQuerysetMixin, View):
    """Inativa marcas em vez de removê-las definitivamente."""

    def post(self, request, *args, **kwargs):
        marca = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        if not marca.ativo:
            messages.info(request, "Marca já estava inativa.")
        else:
            marca.ativo = False
            marca.save(update_fields=["ativo"])
            messages.success(request, "Marca inativada com sucesso.")
        return redirect("produtos:marca_detail", pk=marca.pk)


class ProdutoQuerysetMixin(EmpresaObrigatoriaMixin):
    """Restringe produtos à empresa do usuário logado."""

    model = Produto

    def get_queryset(self):
        return Produto.objects.filter(empresa=self.get_empresa()).select_related("categoria", "marca")


class ProdutoListView(ProdutoQuerysetMixin, ListView):
    """Lista produtos com busca, filtros e paginação."""

    template_name = "produtos/produto_list.html"
    context_object_name = "produtos"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        tipo_controle = self.request.GET.get("tipo_controle", "").strip()

        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca)
                | Q(codigo_interno__icontains=busca)
                | Q(codigo_barras__icontains=busca)
                | Q(categoria__nome__icontains=busca)
                | Q(marca__nome__icontains=busca)
            )
        if status == "ativo":
            queryset = queryset.filter(ativo=True)
        elif status == "inativo":
            queryset = queryset.filter(ativo=False)
        if tipo_controle:
            queryset = queryset.filter(tipo_controle_estoque=tipo_controle)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["busca"] = self.request.GET.get("q", "")
        context["status"] = self.request.GET.get("status", "")
        context["tipo_controle"] = self.request.GET.get("tipo_controle", "")
        context["tipos_controle"] = Produto.TipoControleEstoque.choices
        return context


class ProdutoDetailView(ProdutoQuerysetMixin, DetailView):
    """Exibe detalhes do produto."""

    template_name = "produtos/produto_detail.html"
    context_object_name = "produto"


class ProdutoCreateView(ProdutoQuerysetMixin, CreateView):
    """Cadastra produtos na empresa do usuário logado."""

    form_class = ProdutoForm
    template_name = "produtos/produto_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, "Produto cadastrado com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível salvar o produto. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("produtos:produto_detail", kwargs={"pk": self.object.pk})


class ProdutoUpdateView(ProdutoQuerysetMixin, UpdateView):
    """Edita produtos da empresa do usuário logado."""

    form_class = ProdutoForm
    template_name = "produtos/produto_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Produto atualizado com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível atualizar o produto. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("produtos:produto_detail", kwargs={"pk": self.object.pk})


class ProdutoInativarView(ProdutoQuerysetMixin, View):
    """Inativa produtos em vez de removê-los definitivamente."""

    def post(self, request, *args, **kwargs):
        produto = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        if not produto.ativo:
            messages.info(request, "Produto já estava inativo.")
        else:
            produto.ativo = False
            produto.save(update_fields=["ativo", "atualizado_em"])
            messages.success(request, "Produto inativado com sucesso.")
        return redirect("produtos:produto_detail", pk=produto.pk)
