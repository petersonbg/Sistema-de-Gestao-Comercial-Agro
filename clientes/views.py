"""Views do CRUD de clientes."""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.crud_mixins import EmpresaObrigatoriaMixin

from .forms import ClienteForm
from .models import Cliente


class ClienteQuerysetMixin(EmpresaObrigatoriaMixin):
    """Restringe consultas de clientes à empresa do usuário logado."""

    model = Cliente

    def get_queryset(self):
        return Cliente.objects.filter(empresa=self.get_empresa())


class ClienteListView(ClienteQuerysetMixin, ListView):
    """Lista clientes com busca e paginação."""

    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"
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
                | Q(whatsapp__icontains=busca)
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


class ClienteDetailView(ClienteQuerysetMixin, DetailView):
    """Exibe detalhes do cliente."""

    template_name = "clientes/cliente_detail.html"
    context_object_name = "cliente"


class ClienteCreateView(ClienteQuerysetMixin, CreateView):
    """Cadastra clientes na empresa do usuário logado."""

    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, "Cliente cadastrado com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível salvar o cliente. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("clientes:detail", kwargs={"pk": self.object.pk})


class ClienteUpdateView(ClienteQuerysetMixin, UpdateView):
    """Edita clientes da empresa do usuário logado."""

    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Cliente atualizado com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível atualizar o cliente. Verifique os campos informados.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("clientes:detail", kwargs={"pk": self.object.pk})


class ClienteInativarView(ClienteQuerysetMixin, View):
    """Inativa clientes em vez de removê-los definitivamente."""

    def post(self, request, *args, **kwargs):
        cliente = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        if not cliente.ativo:
            messages.info(request, "Cliente já estava inativo.")
        else:
            cliente.ativo = False
            cliente.save(update_fields=["ativo", "atualizado_em"])
            messages.success(request, "Cliente inativado com sucesso.")
        return redirect("clientes:detail", pk=cliente.pk)
