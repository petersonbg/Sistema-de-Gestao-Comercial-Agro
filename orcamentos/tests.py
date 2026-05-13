"""Testes do fluxo de orçamentos."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from empresas.models import Empresa
from estoque.models import MovimentacaoEstoque
from fornecedores.models import Fornecedor
from produtos.models import Categoria, Produto
from vendas.models import Venda

from .models import Orcamento, OrcamentoItem


class OrcamentoFluxoTests(TestCase):
    """Cobre criação, descontos e conversão de orçamentos."""

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome_fantasia="Agro Teste",
            razao_social="Agro Teste Ltda",
            cnpj="00.000.000/0001-00",
        )
        self.cliente_obj = Cliente.objects.create(empresa=self.empresa, nome="Cliente Teste", cpf_cnpj="123")
        self.categoria = Categoria.objects.create(empresa=self.empresa, nome="Categoria")
        self.fornecedor = Fornecedor.objects.create(empresa=self.empresa, nome="Fornecedor")
        self.produto = Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria,
            nome="Produto simples",
            codigo_interno="P001",
            tipo_controle_estoque=Produto.TipoControleEstoque.SIMPLES,
            preco_custo=Decimal("5.00"),
            preco_venda=Decimal("10.00"),
            estoque_atual=Decimal("10.000"),
        )
        usuario_model = get_user_model()
        self.usuario = usuario_model.objects.create_user(
            username="vendedor",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.VENDEDOR,
        )
        self.cliente = Client()
        self.cliente.force_login(self.usuario)

    def post_orcamento(self, produto=None, quantidade="2.000", desconto_item="0.00", desconto_total="0.00"):
        """Envia o formulário de orçamento com um item preenchido."""
        produto = produto or self.produto
        validade = timezone.localdate() + timezone.timedelta(days=7)
        return self.cliente.post(
            reverse("orcamentos:create"),
            {
                "cliente": self.cliente_obj.pk,
                "validade": validade.isoformat(),
                "desconto": desconto_total,
                "observacoes": "Observação de teste",
                "itens-TOTAL_FORMS": "5",
                "itens-INITIAL_FORMS": "0",
                "itens-MIN_NUM_FORMS": "1",
                "itens-MAX_NUM_FORMS": "1000",
                "itens-0-produto": produto.pk,
                "itens-0-quantidade": quantidade,
                "itens-0-desconto": desconto_item,
                "itens-1-produto": "",
                "itens-1-quantidade": "1.000",
                "itens-1-desconto": "0.00",
                "itens-2-produto": "",
                "itens-2-quantidade": "1.000",
                "itens-2-desconto": "0.00",
                "itens-3-produto": "",
                "itens-3-quantidade": "1.000",
                "itens-3-desconto": "0.00",
                "itens-4-produto": "",
                "itens-4-quantidade": "1.000",
                "itens-4-desconto": "0.00",
            },
        )

    def test_criacao_de_orcamento_nao_baixa_estoque(self):
        """Criar orçamento salva itens e mantém estoque intacto."""
        response = self.post_orcamento()

        self.assertEqual(response.status_code, 302)
        orcamento = Orcamento.objects.get()
        self.assertEqual(orcamento.cliente, self.cliente_obj)
        self.assertEqual(orcamento.status, Orcamento.Status.ABERTO)
        self.assertEqual(orcamento.subtotal, Decimal("20.00"))
        self.assertEqual(orcamento.total, Decimal("20.00"))
        self.assertEqual(orcamento.itens.count(), 1)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_atual, Decimal("10.000"))

    def test_orcamento_com_desconto_por_item_e_total(self):
        """Descontos por item e total compõem o total do orçamento."""
        response = self.post_orcamento(desconto_item="3.00", desconto_total="2.00")

        self.assertEqual(response.status_code, 302)
        orcamento = Orcamento.objects.get()
        item = orcamento.itens.get()
        self.assertEqual(item.subtotal, Decimal("17.00"))
        self.assertEqual(orcamento.subtotal, Decimal("17.00"))
        self.assertEqual(orcamento.desconto, Decimal("2.00"))
        self.assertEqual(orcamento.total, Decimal("15.00"))

    def test_conversao_em_venda_baixa_estoque_e_marca_convertido(self):
        """Converter orçamento cria venda, baixa estoque e impede nova conversão."""
        self.post_orcamento(quantidade="3.000", desconto_item="1.00", desconto_total="2.00")
        orcamento = Orcamento.objects.get()

        response = self.cliente.post(reverse("orcamentos:convert", kwargs={"pk": orcamento.pk}), {"forma_pagamento": Venda.FormaPagamento.PIX})

        self.assertEqual(response.status_code, 302)
        orcamento.refresh_from_db()
        self.produto.refresh_from_db()
        venda = Venda.objects.get()
        self.assertEqual(orcamento.status, Orcamento.Status.CONVERTIDO)
        self.assertEqual(venda.total, Decimal("27.00"))
        self.assertEqual(self.produto.estoque_atual, Decimal("7.000"))
        self.assertEqual(venda.itens.count(), 1)
        self.assertEqual(MovimentacaoEstoque.objects.count(), 1)

        segunda_tentativa = self.cliente.post(
            reverse("orcamentos:convert", kwargs={"pk": orcamento.pk}),
            {"forma_pagamento": Venda.FormaPagamento.PIX},
        )
        self.assertEqual(segunda_tentativa.status_code, 302)
        self.assertEqual(Venda.objects.count(), 1)

    def test_conversao_sem_estoque_suficiente_nao_cria_venda(self):
        """Conversão sem estoque suficiente falha sem baixar saldo."""
        self.post_orcamento(quantidade="11.000")
        orcamento = Orcamento.objects.get()

        response = self.cliente.post(reverse("orcamentos:convert", kwargs={"pk": orcamento.pk}), {"forma_pagamento": Venda.FormaPagamento.PIX})

        self.assertEqual(response.status_code, 302)
        orcamento.refresh_from_db()
        self.produto.refresh_from_db()
        self.assertEqual(orcamento.status, Orcamento.Status.ABERTO)
        self.assertEqual(self.produto.estoque_atual, Decimal("10.000"))
        self.assertEqual(Venda.objects.count(), 0)
