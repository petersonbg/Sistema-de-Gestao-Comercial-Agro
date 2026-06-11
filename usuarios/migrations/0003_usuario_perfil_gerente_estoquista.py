from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_alter_usuario_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuario",
            name="perfil",
            field=models.CharField(
                choices=[
                    ("administrador", "Administrador"),
                    ("gerente", "Gerente"),
                    ("vendedor", "Vendedor"),
                    ("estoquista", "Estoquista"),
                ],
                default="vendedor",
                max_length=20,
            ),
        ),
    ]
