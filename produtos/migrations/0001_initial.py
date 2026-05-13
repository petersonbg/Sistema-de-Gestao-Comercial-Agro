# Generated manually for the initial ERP agro models.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("empresas", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Categoria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100)),
                ("descricao", models.TextField(blank=True)),
                ("ativo", models.BooleanField(default=True)),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="categorias", to="empresas.empresa")),
            ],
            options={"verbose_name": "categoria", "verbose_name_plural": "categorias", "ordering": ["nome"]},
        ),
        migrations.CreateModel(
            name="Marca",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100)),
                ("ativo", models.BooleanField(default=True)),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marcas", to="empresas.empresa")),
            ],
            options={"verbose_name": "marca", "verbose_name_plural": "marcas", "ordering": ["nome"]},
        ),
        migrations.CreateModel(
            name="Produto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=150)),
                ("descricao", models.TextField(blank=True)),
                ("codigo_interno", models.CharField(max_length=50)),
                ("codigo_barras", models.CharField(blank=True, max_length=50, null=True)),
                ("tipo_produto", models.CharField(choices=[("adubo", "Adubo/Fertilizante"), ("peca_mecanica", "Peça mecânica"), ("triciclo", "Triciclo agrícola"), ("ferramenta", "Ferramenta"), ("acessorio", "Acessório"), ("oleo_lubrificante", "Óleo lubrificante"), ("outro", "Outro")], default="outro", max_length=30)),
                ("tipo_controle_estoque", models.CharField(choices=[("simples", "Quantidade simples"), ("lote", "Lote e validade"), ("serial", "Unidade identificada")], default="simples", max_length=10)),
                ("unidade_venda", models.CharField(choices=[("unidade", "Unidade"), ("saco", "Saco"), ("galao", "Galão"), ("bombona", "Bombona"), ("caixa", "Caixa"), ("litro_fechado", "Litro fechado"), ("kg_fechado", "Kg fechado")], default="unidade", max_length=20)),
                ("quantidade_por_embalagem", models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ("unidade_referencia", models.CharField(blank=True, choices=[("kg", "Kg"), ("litro", "Litro"), ("unidade", "Unidade")], max_length=10, null=True)),
                ("preco_custo", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("preco_venda", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("estoque_atual", models.DecimalField(decimal_places=3, default=0, max_digits=12)),
                ("estoque_minimo", models.DecimalField(decimal_places=3, default=0, max_digits=12)),
                ("ativo", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("categoria", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="produtos", to="produtos.categoria")),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="produtos", to="empresas.empresa")),
                ("marca", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="produtos", to="produtos.marca")),
            ],
            options={"verbose_name": "produto", "verbose_name_plural": "produtos", "ordering": ["nome"]},
        ),
        migrations.AddConstraint(model_name="categoria", constraint=models.UniqueConstraint(fields=("empresa", "nome"), name="uniq_categoria_nome_por_empresa")),
        migrations.AddConstraint(model_name="marca", constraint=models.UniqueConstraint(fields=("empresa", "nome"), name="uniq_marca_nome_por_empresa")),
        migrations.AddConstraint(model_name="produto", constraint=models.UniqueConstraint(fields=("empresa", "codigo_interno"), name="uniq_produto_codigo_interno_por_empresa")),
        migrations.AddConstraint(model_name="produto", constraint=models.UniqueConstraint(condition=models.Q(codigo_barras__isnull=False) & ~models.Q(codigo_barras=""), fields=("empresa", "codigo_barras"), name="uniq_produto_codigo_barras_por_empresa")),
        migrations.AddConstraint(model_name="produto", constraint=models.CheckConstraint(check=models.Q(preco_custo__gte=0), name="produto_preco_custo_gte_0")),
        migrations.AddConstraint(model_name="produto", constraint=models.CheckConstraint(check=models.Q(preco_venda__gte=0), name="produto_preco_venda_gte_0")),
        migrations.AddConstraint(model_name="produto", constraint=models.CheckConstraint(check=models.Q(estoque_atual__gte=0), name="produto_estoque_atual_gte_0")),
        migrations.AddConstraint(model_name="produto", constraint=models.CheckConstraint(check=models.Q(estoque_minimo__gte=0), name="produto_estoque_minimo_gte_0")),
    ]
