# Generated manually for sale cancellation fields.

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("vendas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="venda",
            name="cancelado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="vendas_canceladas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="venda",
            name="motivo_cancelamento",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="venda",
            name="cancelado_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
