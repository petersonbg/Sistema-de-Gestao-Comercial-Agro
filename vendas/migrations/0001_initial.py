# Generated manually for the initial ERP agro models.

from django.conf import settings
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("clientes", "0001_initial"),
        ("empresas", "0001_initial"),
        ("estoque", "0001_initial"),
        ("produtos", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Venda",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateTimeField(default=django.utils.timezone.now)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("desconto", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("forma_pagamento", models.CharField(choices=[("dinheiro", "Dinheiro"), ("pix", "Pix"), ("debito", "Cartão de débito"), ("credito", "Cartão de crédito")], max_length=20)),
                ("status", models.CharField(choices=[("finalizada", "Finalizada"), ("cancelada", "Cancelada")], default="finalizada", max_length=20)),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("cliente", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="vendas", to="clientes.cliente")),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vendas", to="empresas.empresa")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vendas", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "venda", "verbose_name_plural": "vendas", "ordering": ["-data", "-id"]},
        ),
        migrations.CreateModel(
            name="VendaItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.DecimalField(decimal_places=3, max_digits=12)),
                ("preco_unitario", models.DecimalField(decimal_places=2, max_digits=12)),
                ("desconto", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12)),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="venda_itens", to="empresas.empresa")),
                ("lote", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="venda_itens", to="estoque.loteestoque")),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="venda_itens", to="produtos.produto")),
                ("unidade_identificada", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="venda_itens", to="estoque.unidadeidentificada")),
                ("venda", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="itens", to="vendas.venda")),
            ],
            options={"verbose_name": "item de venda", "verbose_name_plural": "itens de venda", "ordering": ["id"]},
        ),
        migrations.AddConstraint(model_name="venda", constraint=models.CheckConstraint(check=models.Q(subtotal__gte=0), name="venda_subtotal_gte_0")),
        migrations.AddConstraint(model_name="venda", constraint=models.CheckConstraint(check=models.Q(desconto__gte=0), name="venda_desconto_gte_0")),
        migrations.AddConstraint(model_name="venda", constraint=models.CheckConstraint(check=models.Q(total__gte=0), name="venda_total_gte_0")),
        migrations.AddConstraint(model_name="vendaitem", constraint=models.CheckConstraint(check=models.Q(quantidade__gt=0), name="venda_item_quantidade_gt_0")),
        migrations.AddConstraint(model_name="vendaitem", constraint=models.CheckConstraint(check=models.Q(preco_unitario__gte=0), name="venda_item_preco_unitario_gte_0")),
        migrations.AddConstraint(model_name="vendaitem", constraint=models.CheckConstraint(check=models.Q(desconto__gte=0), name="venda_item_desconto_gte_0")),
        migrations.AddConstraint(model_name="vendaitem", constraint=models.CheckConstraint(check=models.Q(subtotal__gte=0), name="venda_item_subtotal_gte_0")),
    ]
