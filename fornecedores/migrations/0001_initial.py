# Generated manually for the initial ERP agro models.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("empresas", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Fornecedor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=150)),
                ("tipo_pessoa", models.CharField(choices=[("fisica", "Física"), ("juridica", "Jurídica")], default="juridica", max_length=10)),
                ("cpf_cnpj", models.CharField(blank=True, max_length=18)),
                ("telefone", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("endereco", models.CharField(blank=True, max_length=255)),
                ("cidade", models.CharField(blank=True, max_length=100)),
                ("estado", models.CharField(blank=True, max_length=2)),
                ("cep", models.CharField(blank=True, max_length=10)),
                ("observacoes", models.TextField(blank=True)),
                ("ativo", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fornecedores", to="empresas.empresa")),
            ],
            options={"verbose_name": "fornecedor", "verbose_name_plural": "fornecedores", "ordering": ["nome"]},
        ),
        migrations.AddConstraint(
            model_name="fornecedor",
            constraint=models.UniqueConstraint(condition=~models.Q(cpf_cnpj=""), fields=("empresa", "cpf_cnpj"), name="uniq_fornecedor_cpf_cnpj_por_empresa"),
        ),
    ]
