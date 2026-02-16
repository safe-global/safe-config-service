# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0050_alter_chain_block_explorer_uri_address_template_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        help_text="The unique key that identifies this service (e.g., 'cgw', 'frontend')",
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255),
                ),
                (
                    "description",
                    models.CharField(blank=True, default="", max_length=255),
                ),
            ],
        ),
    ]
