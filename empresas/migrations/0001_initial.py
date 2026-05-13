# Generated manually for the initial ERP agro models.

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Empresa",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome_fantasia", models.CharField(max_length=150)),
                ("razao_social", models.CharField(max_length=200)),
                ("cnpj", models.CharField(max_length=18, unique=True)),
                ("telefone", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("endereco", models.CharField(blank=True, max_length=255)),
                ("cidade", models.CharField(blank=True, max_length=100)),
                ("estado", models.CharField(blank=True, max_length=2)),
                ("cep", models.CharField(blank=True, max_length=10)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="empresas/logos/")),
                ("ativo", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "empresa",
                "verbose_name_plural": "empresas",
                "ordering": ["nome_fantasia"],
            },
        ),
    ]
