"""Testes do PDF de recibo de venda."""
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from empresas.models import Empresa
from estoque.models import LoteEstoque, UnidadeIdentificada
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


class VendaFluxoEstoqueTests(TestCase):
    """Cobre venda simples, por lote, serial e cancelamento com estoque."""

    def setUp(self):
        self.empresa = Empresa.objects.create(nome_fantasia="Agro", razao_social="Agro Ltda", cnpj="33")
        self.outra_empresa = Empresa.objects.create(nome_fantasia="Outra", razao_social="Outra Ltda", cnpj="44")
        self.categoria = Categoria.objects.create(empresa=self.empresa, nome="Categoria")
        self.fornecedor = Fornecedor.objects.create(empresa=self.empresa, nome="Fornecedor")
        self.cliente_obj = Cliente.objects.create(empresa=self.empresa, nome="Cliente")
        usuario_model = get_user_model()
        self.admin = usuario_model.objects.create_user(
            username="admin-vendas",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.ADMINISTRADOR,
        )
        self.vendedor = usuario_model.objects.create_user(
            username="vendedor-vendas",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.VENDEDOR,
        )
        self.client = Client()
        self.client.force_login(self.vendedor)

    def finalizar_com_carrinho(self, carrinho, desconto="0.00"):
        session = self.client.session
        session["venda_balcao_carrinho"] = carrinho
        session.save()
        return self.client.post(
            reverse("vendas:balcao"),
            {
                "action": "finalize",
                "cliente": self.cliente_obj.pk,
                "forma_pagamento": Venda.FormaPagamento.PIX,
                "desconto": desconto,
                "observacoes": "Teste",
            },
        )

    def criar_produto(self, nome, codigo, tipo, estoque, preco="10.00"):
        return Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria,
            nome=nome,
            codigo_interno=codigo,
            tipo_controle_estoque=tipo,
            preco_venda=Decimal(preco),
            estoque_atual=Decimal(estoque),
        )

    def test_venda_simples_baixa_estoque_e_bloqueia_total_negativo(self):
        produto = self.criar_produto("Produto simples", "SIMV", Produto.TipoControleEstoque.SIMPLES, "5.000")
        response = self.finalizar_com_carrinho(
            [{"produto_id": produto.pk, "quantidade": "2.000", "desconto": "1.00", "unidade_identificada_id": None}],
            desconto="2.00",
        )
        self.assertEqual(response.status_code, 302)
        produto.refresh_from_db()
        venda = Venda.objects.latest("id")
        self.assertEqual(produto.estoque_atual, Decimal("3.000"))
        self.assertEqual(venda.total, Decimal("17.00"))

        response = self.finalizar_com_carrinho(
            [{"produto_id": produto.pk, "quantidade": "1.000", "desconto": "0.00", "unidade_identificada_id": None}],
            desconto="999.00",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Desconto total não pode ser maior que o subtotal")

    def test_venda_por_lote_usa_fefo_e_nao_vende_lote_vencido(self):
        produto = self.criar_produto("Produto lote", "LOTV", Produto.TipoControleEstoque.LOTE, "5.000")
        vencido = LoteEstoque.objects.create(
            empresa=self.empresa,
            produto=produto,
            fornecedor=self.fornecedor,
            numero_lote="VENCIDO",
            validade=timezone.localdate() - timezone.timedelta(days=1),
            quantidade_inicial=Decimal("3.000"),
            quantidade_atual=Decimal("3.000"),
            data_entrada=timezone.localdate() - timezone.timedelta(days=30),
        )
        valido = LoteEstoque.objects.create(
            empresa=self.empresa,
            produto=produto,
            fornecedor=self.fornecedor,
            numero_lote="VALIDO",
            validade=timezone.localdate() + timezone.timedelta(days=30),
            quantidade_inicial=Decimal("2.000"),
            quantidade_atual=Decimal("2.000"),
            data_entrada=timezone.localdate(),
        )

        response = self.finalizar_com_carrinho(
            [{"produto_id": produto.pk, "quantidade": "2.000", "desconto": "0.00", "unidade_identificada_id": None}]
        )
        self.assertEqual(response.status_code, 302)
        valido.refresh_from_db()
        vencido.refresh_from_db()
        produto.refresh_from_db()
        item = VendaItem.objects.get(lote=valido)
        self.assertEqual(item.quantidade, Decimal("2.000"))
        self.assertEqual(valido.quantidade_atual, Decimal("0.000"))
        self.assertEqual(vencido.quantidade_atual, Decimal("3.000"))
        self.assertEqual(produto.estoque_atual, Decimal("3.000"))

        response = self.finalizar_com_carrinho(
            [{"produto_id": produto.pk, "quantidade": "1.000", "desconto": "0.00", "unidade_identificada_id": None}]
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Estoque por lote insuficiente ou vencido")

    def test_venda_serial_marca_unidade_como_vendida(self):
        produto = self.criar_produto("Produto serial", "SENV", Produto.TipoControleEstoque.SERIAL, "1.000")
        unidade = UnidadeIdentificada.objects.create(
            empresa=self.empresa,
            produto=produto,
            fornecedor=self.fornecedor,
            numero_serie="SER-1",
            status=UnidadeIdentificada.Status.DISPONIVEL,
        )

        response = self.finalizar_com_carrinho(
            [{"produto_id": produto.pk, "quantidade": "1.000", "desconto": "0.00", "unidade_identificada_id": unidade.pk}]
        )
        self.assertEqual(response.status_code, 302)
        unidade.refresh_from_db()
        produto.refresh_from_db()
        self.assertEqual(unidade.status, UnidadeIdentificada.Status.VENDIDO)
        self.assertEqual(produto.estoque_atual, Decimal("0.000"))

    def test_cancelamento_de_venda_devolve_estoque(self):
        produto = self.criar_produto("Produto cancelar", "CANC", Produto.TipoControleEstoque.SIMPLES, "4.000")
        response = self.finalizar_com_carrinho(
            [{"produto_id": produto.pk, "quantidade": "3.000", "desconto": "0.00", "unidade_identificada_id": None}]
        )
        self.assertEqual(response.status_code, 302)
        venda = Venda.objects.latest("id")
        produto.refresh_from_db()
        self.assertEqual(produto.estoque_atual, Decimal("1.000"))

        self.client.force_login(self.admin)
        response = self.client.post(reverse("vendas:cancelar", kwargs={"pk": venda.pk}), {"motivo": "Erro de lançamento"})
        self.assertEqual(response.status_code, 302)
        venda.refresh_from_db()
        produto.refresh_from_db()
        self.assertEqual(venda.status, Venda.Status.CANCELADA)
        self.assertEqual(produto.estoque_atual, Decimal("4.000"))
