"""Views do CRUD de fornecedores."""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.crud_mixins import EmpresaAdministradorObrigatoriaMixin

from .forms import FornecedorForm
from .models import Fornecedor


class FornecedorQuerysetMixin(EmpresaAdministradorObrigatoriaMixin):
    """Restringe consultas de fornecedores à empresa do usuário logado."""

    model = Fornecedor

    def get_queryset(self):
        return Fornecedor.objects.filter(empresa=self.get_empresa())


class FornecedorListView(FornecedorQuerysetMixin, ListView):
    """Lista fornecedores com busca e paginação."""

    template_name = "fornecedores/fornecedor_list.html"
    context_object_name = "fornecedores"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()

        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca)
                | Q(cpf_cnpj__icontains=busca)
                | Q(telefone__icontains=busca)
                | Q(email__icontains=busca)
            )

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


class FornecedorDetailView(FornecedorQuerysetMixin, DetailView):
    """Exibe detalhes do fornecedor."""

    template_name = "fornecedores/fornecedor_detail.html"
    context_object_name = "fornecedor"


class FornecedorCreateView(FornecedorQuerysetMixin, CreateView):
    """Cadastra fornecedores na empresa do usuário logado."""

    form_class = FornecedorForm
    template_name = "fornecedores/fornecedor_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, "Fornecedor cadastrado com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível salvar o fornecedor. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("fornecedores:detail", kwargs={"pk": self.object.pk})


class FornecedorUpdateView(FornecedorQuerysetMixin, UpdateView):
    """Edita fornecedores da empresa do usuário logado."""

    form_class = FornecedorForm
    template_name = "fornecedores/fornecedor_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Fornecedor atualizado com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível atualizar o fornecedor. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("fornecedores:detail", kwargs={"pk": self.object.pk})


class FornecedorInativarView(FornecedorQuerysetMixin, View):
    """Inativa fornecedores em vez de removê-los definitivamente."""

    def post(self, request, *args, **kwargs):
        fornecedor = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        if not fornecedor.ativo:
            messages.info(request, "Fornecedor já estava inativo.")
        else:
            fornecedor.ativo = False
            fornecedor.save(update_fields=["ativo", "atualizado_em"])
            messages.success(request, "Fornecedor inativado com sucesso.")
        return redirect("fornecedores:detail", pk=fornecedor.pk)
