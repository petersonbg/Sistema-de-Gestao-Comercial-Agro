"""Testes básicos de entrada de estoque."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from empresas.models import Empresa
from fornecedores.models import Fornecedor
from produtos.models import Categoria, Produto

from .models import LoteEstoque, MovimentacaoEstoque


class EntradaEstoqueTests(TestCase):
    """Cobre entrada simples e por lote com isolamento por empresa."""

    def setUp(self):
        self.empresa = Empresa.objects.create(nome_fantasia="Agro", razao_social="Agro Ltda", cnpj="11")
        self.outra_empresa = Empresa.objects.create(nome_fantasia="Outra", razao_social="Outra Ltda", cnpj="22")
        self.categoria = Categoria.objects.create(empresa=self.empresa, nome="Categoria")
        self.outra_categoria = Categoria.objects.create(empresa=self.outra_empresa, nome="Categoria")
        self.fornecedor = Fornecedor.objects.create(empresa=self.empresa, nome="Fornecedor")
        self.produto_simples = Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria,
            nome="Produto simples",
            codigo_interno="SIM",
            tipo_controle_estoque=Produto.TipoControleEstoque.SIMPLES,
            preco_venda=Decimal("10.00"),
            estoque_atual=Decimal("1.000"),
        )
        self.produto_lote = Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria,
            nome="Produto lote",
            codigo_interno="LOT",
            tipo_controle_estoque=Produto.TipoControleEstoque.LOTE,
            preco_venda=Decimal("20.00"),
            estoque_atual=Decimal("0.000"),
        )
        self.produto_outra_empresa = Produto.objects.create(
            empresa=self.outra_empresa,
            categoria=self.outra_categoria,
            nome="Produto externo",
            codigo_interno="EXT",
            estoque_atual=Decimal("0.000"),
        )
        usuario_model = get_user_model()
        self.admin = usuario_model.objects.create_user(
            username="admin",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.ADMINISTRADOR,
        )
        self.vendedor = usuario_model.objects.create_user(
            username="vendedor",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.VENDEDOR,
        )
        self.client = Client()
        self.client.force_login(self.admin)

    def test_entrada_estoque_simples_soma_saldo_e_movimenta(self):
        response = self.client.post(
            reverse("estoque:entrada"),
            {
                "produto": self.produto_simples.pk,
                "fornecedor": self.fornecedor.pk,
                "quantidade": "4.000",
                "preco_custo": "7.50",
                "observacao": "Compra",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.produto_simples.refresh_from_db()
        self.assertEqual(self.produto_simples.estoque_atual, Decimal("5.000"))
        self.assertEqual(MovimentacaoEstoque.objects.filter(produto=self.produto_simples).count(), 1)

    def test_entrada_por_lote_cria_lote_e_soma_saldo(self):
        validade = timezone.localdate() + timezone.timedelta(days=120)
        response = self.client.post(
            reverse("estoque:entrada"),
            {
                "produto": self.produto_lote.pk,
                "fornecedor": self.fornecedor.pk,
                "numero_lote": "L001",
                "validade": validade.isoformat(),
                "quantidade": "3.000",
                "preco_custo": "12.00",
                "observacao": "Entrada lote",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.produto_lote.refresh_from_db()
        lote = LoteEstoque.objects.get(produto=self.produto_lote, numero_lote="L001")
        self.assertEqual(lote.quantidade_atual, Decimal("3.000"))
        self.assertEqual(self.produto_lote.estoque_atual, Decimal("3.000"))
        self.assertEqual(MovimentacaoEstoque.objects.filter(lote=lote).count(), 1)

    def test_vendedor_nao_acessa_entrada_e_produto_de_outra_empresa_nao_entra(self):
        self.client.force_login(self.vendedor)
        response = self.client.get(reverse("estoque:entrada"))
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("estoque:entrada"),
            {"produto": self.produto_outra_empresa.pk, "quantidade": "1.000", "preco_custo": "1.00"},
        )
        self.assertEqual(response.status_code, 404)
