"""Testes do PDF de recibo de venda."""
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from empresas.models import Empresa
from estoque.models import LoteEstoque
from fornecedores.models import Fornecedor
from produtos.models import Categoria, Produto

from .models import Venda, VendaItem


class FakeHTML:
    """Substituto de WeasyPrint para testar geração da resposta PDF."""

    rendered_strings = []

    def __init__(self, string, base_url):
        self.rendered_strings.append(string)
        self.base_url = base_url

    def write_pdf(self):
        return b"%PDF-1.4\nrecibo"


class VendaPdfTests(TestCase):
    """Cobre o PDF de recibo da venda."""

    def setUp(self):
        FakeHTML.rendered_strings = []
        self.empresa = Empresa.objects.create(
            nome_fantasia="Agro Teste",
            razao_social="Agro Teste Ltda",
            cnpj="00.000.000/0001-00",
            telefone="(11) 99999-9999",
        )
        self.cliente_obj = Cliente.objects.create(empresa=self.empresa, nome="Cliente Teste", cpf_cnpj="123")
        self.categoria = Categoria.objects.create(empresa=self.empresa, nome="Categoria")
        self.fornecedor = Fornecedor.objects.create(empresa=self.empresa, nome="Fornecedor")
        self.produto = Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria,
            nome="Produto com lote",
            codigo_interno="P001",
            tipo_controle_estoque=Produto.TipoControleEstoque.LOTE,
            preco_venda=Decimal("10.00"),
            estoque_atual=Decimal("5.000"),
        )
        self.lote = LoteEstoque.objects.create(
            empresa=self.empresa,
            produto=self.produto,
            fornecedor=self.fornecedor,
            numero_lote="LOTE-INTERNO",
            validade=timezone.localdate() + timezone.timedelta(days=30),
            quantidade_inicial=Decimal("5.000"),
            quantidade_atual=Decimal("4.000"),
            data_entrada=timezone.localdate(),
        )
        usuario_model = get_user_model()
        self.usuario = usuario_model.objects.create_user(
            username="vendedor",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.VENDEDOR,
        )
        self.venda = Venda.objects.create(
            empresa=self.empresa,
            cliente=self.cliente_obj,
            usuario=self.usuario,
            subtotal=Decimal("20.00"),
            desconto=Decimal("2.00"),
            total=Decimal("18.00"),
            forma_pagamento=Venda.FormaPagamento.PIX,
            observacoes="Entregar na fazenda.",
        )
        VendaItem.objects.create(
            empresa=self.empresa,
            venda=self.venda,
            produto=self.produto,
            lote=self.lote,
            quantidade=Decimal("2.000"),
            preco_unitario=Decimal("10.00"),
            desconto=Decimal("0.00"),
            subtotal=Decimal("20.00"),
        )
        self.client = Client()
        self.client.force_login(self.usuario)

    @patch("core.pdf.get_weasy_html", return_value=FakeHTML)
    def test_pdf_recibo_de_venda_abre_inline_sem_exibir_lote(self, _html):
        """Recibo retorna PDF inline com dados principais e sem lote/validade."""
        response = self.client.get(reverse("vendas:recibo_pdf", kwargs={"pk": self.venda.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("inline", response["Content-Disposition"])
        self.assertIn("recibo-venda", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))
        html = FakeHTML.rendered_strings[-1]
        self.assertIn("Recibo de venda", html)
        self.assertIn("Agro Teste", html)
        self.assertIn("Produto com lote", html)
        self.assertIn("Forma de pagamento", html)
        self.assertNotIn("LOTE-INTERNO", html)
        self.assertNotIn("Validade", html)
