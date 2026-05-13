# Generated manually for the initial ERP agro models.

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("empresas", "0001_initial"),
        ("fornecedores", "0001_initial"),
        ("produtos", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LoteEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_lote", models.CharField(max_length=80)),
                ("validade", models.DateField()),
                ("quantidade_inicial", models.DecimalField(decimal_places=3, max_digits=12)),
                ("quantidade_atual", models.DecimalField(decimal_places=3, max_digits=12)),
                ("preco_custo", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("data_entrada", models.DateField()),
                ("ativo", models.BooleanField(default=True)),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lotes_estoque", to="empresas.empresa")),
                ("fornecedor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lotes_estoque", to="fornecedores.fornecedor")),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lotes_estoque", to="produtos.produto")),
            ],
            options={"verbose_name": "lote de estoque", "verbose_name_plural": "lotes de estoque", "ordering": ["validade", "numero_lote"]},
        ),
        migrations.CreateModel(
            name="UnidadeIdentificada",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_serie", models.CharField(blank=True, max_length=100)),
                ("chassi", models.CharField(blank=True, max_length=100)),
                ("modelo", models.CharField(blank=True, max_length=100)),
                ("cor", models.CharField(blank=True, max_length=50)),
                ("ano_modelo", models.PositiveIntegerField(blank=True, null=True)),
                ("preco_custo", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("preco_venda", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("status", models.CharField(choices=[("disponivel", "Disponível"), ("reservado", "Reservado"), ("vendido", "Vendido"), ("inativo", "Inativo")], default="disponivel", max_length=20)),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="unidades_identificadas", to="empresas.empresa")),
                ("fornecedor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="unidades_identificadas", to="fornecedores.fornecedor")),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="unidades_identificadas", to="produtos.produto")),
            ],
            options={"verbose_name": "unidade identificada", "verbose_name_plural": "unidades identificadas", "ordering": ["produto__nome", "numero_serie", "chassi"]},
        ),
        migrations.CreateModel(
            name="MovimentacaoEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo_movimentacao", models.CharField(choices=[("entrada", "Entrada"), ("saida", "Saída"), ("ajuste", "Ajuste"), ("cancelamento_venda", "Cancelamento de venda")], max_length=20)),
                ("quantidade", models.DecimalField(decimal_places=3, max_digits=12)),
                ("observacao", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="movimentacoes_estoque", to="empresas.empresa")),
                ("lote", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes", to="estoque.loteestoque")),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes_estoque", to="produtos.produto")),
                ("unidade_identificada", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes", to="estoque.unidadeidentificada")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes_estoque", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "movimentação de estoque", "verbose_name_plural": "movimentações de estoque", "ordering": ["-criado_em"]},
        ),
        migrations.AddConstraint(model_name="loteestoque", constraint=models.UniqueConstraint(fields=("empresa", "produto", "numero_lote"), name="uniq_lote_produto_por_empresa")),
        migrations.AddConstraint(model_name="loteestoque", constraint=models.CheckConstraint(check=models.Q(quantidade_inicial__gte=0), name="lote_quantidade_inicial_gte_0")),
        migrations.AddConstraint(model_name="loteestoque", constraint=models.CheckConstraint(check=models.Q(quantidade_atual__gte=0), name="lote_quantidade_atual_gte_0")),
        migrations.AddConstraint(model_name="loteestoque", constraint=models.CheckConstraint(check=models.Q(preco_custo__gte=0), name="lote_preco_custo_gte_0")),
        migrations.AddConstraint(model_name="unidadeidentificada", constraint=models.UniqueConstraint(condition=~models.Q(numero_serie=""), fields=("empresa", "numero_serie"), name="uniq_unidade_numero_serie_por_empresa")),
        migrations.AddConstraint(model_name="unidadeidentificada", constraint=models.UniqueConstraint(condition=~models.Q(chassi=""), fields=("empresa", "chassi"), name="uniq_unidade_chassi_por_empresa")),
        migrations.AddConstraint(model_name="unidadeidentificada", constraint=models.CheckConstraint(check=models.Q(preco_custo__gte=0), name="unidade_preco_custo_gte_0")),
        migrations.AddConstraint(model_name="unidadeidentificada", constraint=models.CheckConstraint(check=models.Q(preco_venda__gte=0), name="unidade_preco_venda_gte_0")),
        migrations.AddConstraint(model_name="movimentacaoestoque", constraint=models.CheckConstraint(check=models.Q(quantidade__gt=0), name="movimentacao_quantidade_gt_0")),
    ]
