"""Testes dos relatórios básicos."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from empresas.models import Empresa
from estoque.models import LoteEstoque
from fornecedores.models import Fornecedor
from produtos.models import Categoria, Produto
from vendas.models import Venda, VendaItem


class RelatoriosBasicosTests(TestCase):
    """Cobre consultas principais e isolamento por empresa."""

    def setUp(self):
        self.empresa = Empresa.objects.create(nome_fantasia="Agro Matriz", razao_social="Agro Matriz Ltda", cnpj="11")
        self.outra_empresa = Empresa.objects.create(nome_fantasia="Outra Agro", razao_social="Outra Agro Ltda", cnpj="22")
        self.categoria = Categoria.objects.create(empresa=self.empresa, nome="Fertilizantes")
        self.outra_categoria = Categoria.objects.create(empresa=self.outra_empresa, nome="Outros")
        self.fornecedor = Fornecedor.objects.create(empresa=self.empresa, nome="Fornecedor Matriz")
        self.cliente_obj = Cliente.objects.create(empresa=self.empresa, nome="Cliente Matriz")
        self.outro_cliente = Cliente.objects.create(empresa=self.outra_empresa, nome="Cliente Outra")
        self.produto_baixo = Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria,
            nome="Adubo baixo",
            codigo_interno="ADB",
            tipo_controle_estoque=Produto.TipoControleEstoque.SIMPLES,
            preco_venda=Decimal("50.00"),
            estoque_atual=Decimal("2.000"),
            estoque_minimo=Decimal("5.000"),
        )
        self.produto_ok = Produto.objects.create(
            empresa=self.empresa,
            categoria=self.categoria,
            nome="Adubo ok",
            codigo_interno="ADO",
            tipo_controle_estoque=Produto.TipoControleEstoque.SIMPLES,
            preco_venda=Decimal("30.00"),
            estoque_atual=Decimal("20.000"),
            estoque_minimo=Decimal("5.000"),
        )
        self.produto_outra_empresa = Produto.objects.create(
            empresa=self.outra_empresa,
            categoria=self.outra_categoria,
            nome="Produto externo",
            codigo_interno="EXT",
            preco_venda=Decimal("99.00"),
            estoque_atual=Decimal("1.000"),
            estoque_minimo=Decimal("10.000"),
        )
        hoje = timezone.localdate()
        self.lote_proximo = LoteEstoque.objects.create(
            empresa=self.empresa,
            produto=self.produto_ok,
            fornecedor=self.fornecedor,
            numero_lote="PROX",
            validade=hoje + timezone.timedelta(days=30),
            quantidade_inicial=Decimal("10.000"),
            quantidade_atual=Decimal("4.000"),
            data_entrada=hoje,
        )
        self.lote_vencido = LoteEstoque.objects.create(
            empresa=self.empresa,
            produto=self.produto_baixo,
            fornecedor=self.fornecedor,
            numero_lote="VENC",
            validade=hoje - timezone.timedelta(days=1),
            quantidade_inicial=Decimal("10.000"),
            quantidade_atual=Decimal("3.000"),
            data_entrada=hoje - timezone.timedelta(days=60),
        )
        usuario_model = get_user_model()
        self.usuario = usuario_model.objects.create_user(
            username="admin",
            password="senha",
            empresa=self.empresa,
            perfil=usuario_model.Perfil.ADMINISTRADOR,
        )
        self.outro_usuario = usuario_model.objects.create_user(
            username="outro",
            password="senha",
            empresa=self.outra_empresa,
            perfil=usuario_model.Perfil.ADMINISTRADOR,
        )
        self.venda_pix = Venda.objects.create(
            empresa=self.empresa,
            cliente=self.cliente_obj,
            usuario=self.usuario,
            subtotal=Decimal("100.00"),
            desconto=Decimal("0.00"),
            total=Decimal("100.00"),
            forma_pagamento=Venda.FormaPagamento.PIX,
            status=Venda.Status.FINALIZADA,
        )
        VendaItem.objects.create(
            empresa=self.empresa,
            venda=self.venda_pix,
            produto=self.produto_baixo,
            quantidade=Decimal("2.000"),
            preco_unitario=Decimal("50.00"),
            desconto=Decimal("0.00"),
            subtotal=Decimal("100.00"),
        )
        self.venda_cancelada = Venda.objects.create(
            empresa=self.empresa,
            cliente=self.cliente_obj,
            usuario=self.usuario,
            subtotal=Decimal("30.00"),
            desconto=Decimal("0.00"),
            total=Decimal("30.00"),
            forma_pagamento=Venda.FormaPagamento.DINHEIRO,
            status=Venda.Status.CANCELADA,
        )
        Venda.objects.create(
            empresa=self.outra_empresa,
            cliente=self.outro_cliente,
            usuario=self.outro_usuario,
            subtotal=Decimal("999.00"),
            desconto=Decimal("0.00"),
            total=Decimal("999.00"),
            forma_pagamento=Venda.FormaPagamento.PIX,
            status=Venda.Status.FINALIZADA,
        )
        self.client = Client()
        self.client.force_login(self.usuario)

    def test_vendas_do_dia_filtra_empresa(self):
        response = self.client.get(reverse("relatorios:vendas_dia"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente Matriz")
        self.assertContains(response, "#%s" % self.venda_pix.pk)
        self.assertNotContains(response, "Cliente Outra")

    def test_vendas_periodo_totaliza_finalizadas_por_pagamento(self):
        hoje = timezone.localdate().isoformat()
        response = self.client.get(reverse("relatorios:vendas_periodo"), {"data_inicial": hoje, "data_final": hoje})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "R$ 100")
        self.assertContains(response, "Pix")
        self.assertContains(response, "Cancelada")
        self.assertNotContains(response, "999.00")

    def test_relatorios_de_estoque_e_vencimento(self):
        estoque_baixo = self.client.get(reverse("relatorios:estoque_baixo"))
        self.assertContains(estoque_baixo, "Adubo baixo")
        self.assertNotContains(estoque_baixo, "Adubo ok")
        self.assertNotContains(estoque_baixo, "Produto externo")

        proximos = self.client.get(reverse("relatorios:proximos_vencimento"))
        self.assertContains(proximos, "PROX")
        self.assertNotContains(proximos, "VENC")

        vencidos = self.client.get(reverse("relatorios:vencidos"))
        self.assertContains(vencidos, "VENC")
        self.assertNotContains(vencidos, "PROX")

    def test_produtos_mais_vendidos_por_periodo(self):
        hoje = timezone.localdate().isoformat()
        response = self.client.get(reverse("relatorios:mais_vendidos"), {"data_inicial": hoje, "data_final": hoje})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adubo baixo")
        self.assertContains(response, ">2<")
        self.assertContains(response, "R$ 100")
        self.assertNotContains(response, "Produto externo")
