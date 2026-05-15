"""Testes básicos de cadastro e isolamento de produtos."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from empresas.models import Empresa

from .models import Categoria, Produto


class ProdutoCadastroTests(TestCase):
    """Cobre cadastro, unicidade por empresa e isolamento de produtos."""

    def setUp(self):
        self.empresa = Empresa.objects.create(nome_fantasia="Agro", razao_social="Agro Ltda", cnpj="11")
        self.outra_empresa = Empresa.objects.create(nome_fantasia="Outra", razao_social="Outra Ltda", cnpj="22")
        self.categoria = Categoria.objects.create(empresa=self.empresa, nome="Categoria")
        self.outra_categoria = Categoria.objects.create(empresa=self.outra_empresa, nome="Categoria")
        usuario_model = get_user_model()
        self.usuario = usuario_model.objects.create_user(
            username="vendedor",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.VENDEDOR,
        )
        self.client = Client()
        self.client.force_login(self.usuario)

    def dados_produto(self, **overrides):
        dados = {
            "categoria": self.categoria.pk,
            "marca": "",
            "nome": "Adubo teste",
            "descricao": "",
            "codigo_interno": "ADB001",
            "codigo_barras": "789000000001",
            "tipo_produto": Produto.TipoProduto.ADUBO,
            "tipo_controle_estoque": Produto.TipoControleEstoque.SIMPLES,
            "unidade_venda": Produto.UnidadeVenda.SACO,
            "quantidade_por_embalagem": "50.000",
            "unidade_referencia": Produto.UnidadeReferencia.KG,
            "preco_custo": "10.00",
            "preco_venda": "20.00",
            "estoque_atual": "0.000",
            "estoque_minimo": "2.000",
        }
        dados.update(overrides)
        return dados

    def test_cadastro_de_produto_filtra_empresa_e_valida_codigos(self):
        response = self.client.post(reverse("produtos:produto_create"), self.dados_produto())
        self.assertEqual(response.status_code, 302)
        produto = Produto.objects.get(empresa=self.empresa, codigo_interno="ADB001")
        self.assertEqual(produto.codigo_barras, "789000000001")
        self.assertEqual(produto.estoque_atual, Decimal("0.000"))

        duplicado_interno = self.client.post(
            reverse("produtos:produto_create"),
            self.dados_produto(nome="Outro", codigo_barras="789000000002"),
        )
        self.assertEqual(duplicado_interno.status_code, 200)
        self.assertContains(duplicado_interno, "Já existe um produto com este código interno")

        duplicado_barras = self.client.post(
            reverse("produtos:produto_create"),
            self.dados_produto(nome="Outro", codigo_interno="ADB002"),
        )
        self.assertEqual(duplicado_barras.status_code, 200)
        self.assertContains(duplicado_barras, "Já existe um produto com este código de barras")

        Produto.objects.create(
            empresa=self.outra_empresa,
            categoria=self.outra_categoria,
            nome="Produto de outra empresa",
            codigo_interno="EXT001",
            codigo_barras="789999999999",
            preco_venda=Decimal("1.00"),
        )
        response = self.client.get(reverse("produtos:produto_list"), {"q": "EXT001"})
        self.assertNotContains(response, "Produto de outra empresa")
