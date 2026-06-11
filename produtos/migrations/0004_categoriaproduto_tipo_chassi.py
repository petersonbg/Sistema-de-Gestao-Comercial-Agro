from django.db import migrations, models
from django.utils import timezone


def migrar_produtos_com_chassi(apps, schema_editor):
    CategoriaProduto = apps.get_model("produtos", "CategoriaProduto")
    Produto = apps.get_model("produtos", "Produto")

    empresas_ids = Produto.objects.exclude(chassi__isnull=True).exclude(chassi="").values_list(
        "empresa_id", flat=True
    ).distinct()
    for empresa_id in empresas_ids:
        categoria_veiculos = CategoriaProduto.objects.filter(
            empresa_id=empresa_id, nome__iexact="Veículos"
        ).first()
        if categoria_veiculos is None:
            categoria_veiculos = CategoriaProduto.objects.create(
                empresa_id=empresa_id,
                nome="Veículos",
                descricao="Categoria criada automaticamente para preservar produtos com chassi.",
                tipo="VEICULOS",
                ativo=True,
            )
        elif categoria_veiculos.tipo != "VEICULOS":
            categoria_veiculos.tipo = "VEICULOS"
            categoria_veiculos.save(update_fields=["tipo", "atualizado_em"])

        Produto.objects.filter(empresa_id=empresa_id).exclude(chassi__isnull=True).exclude(chassi="").update(
            categoria_id=categoria_veiculos.pk
        )


class Migration(migrations.Migration):
    dependencies = [
        ("produtos", "0003_produto_chassi_alter_produto_codigo_interno_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Categoria",
            new_name="CategoriaProduto",
        ),
        migrations.AddField(
            model_name="categoriaproduto",
            name="tipo",
            field=models.CharField(
                choices=[("GERAL", "Geral"), ("VEICULOS", "Veículos")],
                default="GERAL",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="categoriaproduto",
            name="criado_em",
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="categoriaproduto",
            name="atualizado_em",
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name="categoriaproduto",
            options={
                "ordering": ["nome"],
                "verbose_name": "categoria de produto",
                "verbose_name_plural": "categorias de produtos",
            },
        ),
        migrations.RunPython(migrar_produtos_com_chassi, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name="produto",
            name="uniq_produto_chassi_por_empresa",
        ),
        migrations.AlterField(
            model_name="produto",
            name="chassi",
            field=models.CharField("Chassi", blank=True, max_length=50, null=True),
        ),
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.UniqueConstraint(
                condition=models.Q(chassi__isnull=False) & ~models.Q(chassi=""),
                fields=("empresa", "chassi"),
                name="uniq_produto_chassi_por_empresa",
            ),
        ),
    ]
