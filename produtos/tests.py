"""Testes de categorias, cadastro e isolamento de produtos."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from empresas.models import Empresa

from .models import CategoriaProduto, Produto


class ProdutoCadastroTests(TestCase):
    """Cobre categorias, regras de chassi, filtros e isolamento de produtos."""

    def setUp(self):
        self.empresa = Empresa.objects.create(nome_fantasia="Agro", razao_social="Agro Ltda", cnpj="11")
        self.outra_empresa = Empresa.objects.create(nome_fantasia="Outra", razao_social="Outra Ltda", cnpj="22")
        self.categoria_geral = CategoriaProduto.objects.create(
            empresa=self.empresa,
            nome="Insumos",
            tipo=CategoriaProduto.Tipo.GERAL,
        )
        self.categoria_veiculos = CategoriaProduto.objects.create(
            empresa=self.empresa,
            nome="Veículos",
            tipo=CategoriaProduto.Tipo.VEICULOS,
        )
        self.categoria_inativa = CategoriaProduto.objects.create(
            empresa=self.empresa,
            nome="Descontinuados",
            tipo=CategoriaProduto.Tipo.GERAL,
            ativo=False,
        )
        self.outra_categoria = CategoriaProduto.objects.create(
            empresa=self.outra_empresa,
            nome="Categoria",
        )
        usuario_model = get_user_model()
        self.usuario = usuario_model.objects.create_user(
            username="vendedor",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.VENDEDOR,
        )
        self.administrador = usuario_model.objects.create_user(
            username="administrador",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.ADMINISTRADOR,
            is_staff=True,
        )
        self.gerente = usuario_model.objects.create_user(
            username="gerente",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.GERENTE,
        )
        self.estoquista = usuario_model.objects.create_user(
            username="estoquista",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.ESTOQUISTA,
        )
        self.client = Client()
        self.client.force_login(self.usuario)

    def dados_produto(self, **overrides):
        dados = {
            "categoria": self.categoria_geral.pk,
            "marca": "",
            "nome": "Adubo teste",
            "descricao": "",
            "codigo_barras": "789000000001",
            "chassi": "CHASSI-INDEVIDO",
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

    def test_cria_categorias_geral_e_veiculos(self):
        self.assertEqual(self.categoria_geral.tipo, CategoriaProduto.Tipo.GERAL)
        self.assertEqual(self.categoria_veiculos.tipo, CategoriaProduto.Tipo.VEICULOS)
        self.assertTrue(self.categoria_geral.ativo)
        self.assertIsNotNone(self.categoria_geral.criado_em)

    def test_formulario_exibe_apenas_categorias_ativas(self):
        response = self.client.get(reverse("produtos:produto_create"))
        self.assertContains(response, self.categoria_geral.nome)
        self.assertContains(response, self.categoria_veiculos.nome)
        self.assertNotContains(response, self.categoria_inativa.nome)
        self.assertContains(response, "Disponível apenas para produtos da categoria Veículos.")

    def test_produto_geral_descarta_chassi_no_formulario_e_no_modelo(self):
        response = self.client.post(reverse("produtos:produto_create"), self.dados_produto())
        self.assertEqual(response.status_code, 302)
        produto = Produto.objects.get(empresa=self.empresa, codigo_interno="PROD000001")
        self.assertIsNone(produto.chassi)

        produto.chassi = "TENTATIVA-DIRETA"
        produto.save()
        produto.refresh_from_db()
        self.assertIsNone(produto.chassi)

    def test_produto_veiculo_aceita_chassi(self):
        response = self.client.post(
            reverse("produtos:produto_create"),
            self.dados_produto(
                categoria=self.categoria_veiculos.pk,
                nome="Triciclo",
                codigo_barras="789000000002",
                chassi="abc-123",
                tipo_produto=Produto.TipoProduto.TRICICLO,
            ),
        )
        self.assertEqual(response.status_code, 302)
        produto = Produto.objects.get(nome="Triciclo")
        self.assertEqual(produto.chassi, "ABC-123")

    def test_filtro_por_categoria_e_busca_por_chassi(self):
        Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria_geral,
            nome="Fertilizante",
            codigo_interno="GERAL001",
            codigo_barras="100",
        )
        Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria_veiculos,
            nome="Triciclo",
            codigo_interno="VEIC001",
            codigo_barras="200",
            chassi="CHASSI-200",
        )

        response = self.client.get(reverse("produtos:produto_list"), {"categoria": self.categoria_veiculos.pk})
        self.assertContains(response, "Triciclo")
        self.assertNotContains(response, "Fertilizante")

        response = self.client.get(reverse("produtos:produto_list"), {"q": "CHASSI-200"})
        self.assertContains(response, "Triciclo")

    def test_isolamento_por_empresa_permanece_ativo(self):
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

    def test_apenas_administrador_edita_categoria_e_gerente_visualiza(self):
        self.client.force_login(self.usuario)
        self.assertEqual(
            self.client.get(reverse("produtos:categoria_update", args=[self.categoria_geral.pk])).status_code,
            403,
        )
        self.client.force_login(self.estoquista)
        self.assertEqual(
            self.client.get(reverse("produtos:categoria_update", args=[self.categoria_geral.pk])).status_code,
            403,
        )

        self.client.force_login(self.gerente)
        response = self.client.get(reverse("produtos:categoria_list"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("produtos:categoria_update", args=[self.categoria_geral.pk]))
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.administrador)
        response = self.client.post(
            reverse("produtos:categoria_create"),
            {"nome": "Peças", "descricao": "Peças gerais", "tipo": CategoriaProduto.Tipo.GERAL, "ativo": True},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CategoriaProduto.objects.filter(empresa=self.empresa, nome="Peças").exists())

    def test_admin_busca_produto_por_chassi(self):
        Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria_veiculos,
            nome="Veículo administrativo",
            codigo_interno="ADM001",
            chassi="ADMIN-CHASSI",
        )
        self.client.force_login(self.administrador)
        response = self.client.get(reverse("admin:produtos_produto_changelist"), {"q": "ADMIN-CHASSI"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Veículo administrativo")
