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
        ("produtos", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Orcamento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateTimeField(default=django.utils.timezone.now)),
                ("validade", models.DateField()),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("desconto", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("status", models.CharField(choices=[("aberto", "Aberto"), ("aprovado", "Aprovado"), ("convertido", "Convertido"), ("cancelado", "Cancelado"), ("vencido", "Vencido")], default="aberto", max_length=20)),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orcamentos", to="clientes.cliente")),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="orcamentos", to="empresas.empresa")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orcamentos", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "orçamento", "verbose_name_plural": "orçamentos", "ordering": ["-data", "-id"]},
        ),
        migrations.CreateModel(
            name="OrcamentoItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.DecimalField(decimal_places=3, max_digits=12)),
                ("preco_unitario", models.DecimalField(decimal_places=2, max_digits=12)),
                ("desconto", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12)),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="orcamento_itens", to="empresas.empresa")),
                ("orcamento", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="itens", to="orcamentos.orcamento")),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orcamento_itens", to="produtos.produto")),
            ],
            options={"verbose_name": "item de orçamento", "verbose_name_plural": "itens de orçamento", "ordering": ["id"]},
        ),
        migrations.AddConstraint(model_name="orcamento", constraint=models.CheckConstraint(check=models.Q(subtotal__gte=0), name="orcamento_subtotal_gte_0")),
        migrations.AddConstraint(model_name="orcamento", constraint=models.CheckConstraint(check=models.Q(desconto__gte=0), name="orcamento_desconto_gte_0")),
        migrations.AddConstraint(model_name="orcamento", constraint=models.CheckConstraint(check=models.Q(total__gte=0), name="orcamento_total_gte_0")),
        migrations.AddConstraint(model_name="orcamentoitem", constraint=models.CheckConstraint(check=models.Q(quantidade__gt=0), name="orcamento_item_quantidade_gt_0")),
        migrations.AddConstraint(model_name="orcamentoitem", constraint=models.CheckConstraint(check=models.Q(preco_unitario__gte=0), name="orcamento_item_preco_unitario_gte_0")),
        migrations.AddConstraint(model_name="orcamentoitem", constraint=models.CheckConstraint(check=models.Q(desconto__gte=0), name="orcamento_item_desconto_gte_0")),
        migrations.AddConstraint(model_name="orcamentoitem", constraint=models.CheckConstraint(check=models.Q(subtotal__gte=0), name="orcamento_item_subtotal_gte_0")),
    ]
