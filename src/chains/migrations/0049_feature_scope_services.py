# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0048_service"),
    ]

    operations = [
        migrations.AddField(
            model_name="Feature",
            name="scope",
            field=models.CharField(
                choices=[
                    ("GLOBAL", "Global (applies to all chains)"),
                    ("PER_CHAIN", "Per-chain (applies only to selected chains)"),
                ],
                default="PER_CHAIN",
                help_text="Global applies to all chains. Per-chain limits the feature to selected chains.",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="Feature",
            name="services",
            field=models.ManyToManyField(
                blank=True,
                help_text="Services that have access to this feature.",
                to="chains.service",
            ),
        ),
        migrations.AlterField(
            model_name="Feature",
            name="chains",
            field=models.ManyToManyField(
                blank=True,
                help_text="Chains where this feature is enabled. Used only when scope is per-chain.",
                to="chains.Chain",
            ),
        ),
    ]
