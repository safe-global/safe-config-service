from django.db import migrations, models


def populate_chains(apps, schema_editor):
    Chain = apps.get_model("safe_apps", "Chain")
    chains_data = [
        {"chain_id": 1, "name": "Ethereum"},
        {"chain_id": 100, "name": "Gnosis Chain"},
        {"chain_id": 137, "name": "Polygon"},
        {"chain_id": 1101, "name": "Polygon zkEVM"},
        {"chain_id": 56, "name": "BNB Chain"},
        {"chain_id": 42161, "name": "Arbitrum"},
        {"chain_id": 10, "name": "Optimism"},
        {"chain_id": 8453, "name": "Base"},
        {"chain_id": 59144, "name": "Linea"},
        {"chain_id": 324, "name": "zkSync Era"},
        {"chain_id": 534352, "name": "Scroll"},
        {"chain_id": 196, "name": "X Layer"},
        {"chain_id": 42220, "name": "Celo"},
        {"chain_id": 43114, "name": "Avalanche"},
        {"chain_id": 81457, "name": "Blast"},
        {"chain_id": 1313161554, "name": "Aurora"},
        {"chain_id": 11155111, "name": "Sepolia"},
        {"chain_id": 84532, "name": "Base Sepolia"},
        {"chain_id": 10200, "name": "Gnosis Chiado"},
    ]

    for chain in chains_data:
        Chain.objects.get_or_create(
            chain_id=chain["chain_id"], defaults={"name": chain["name"]}
        )


def reverse_populate_chains(apps, schema_editor):
    Chain = apps.get_model("safe_apps", "Chain")
    Chain.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("safe_apps", "0014_alter_safeapp_icon_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="Chain",
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
                ("chain_id", models.PositiveIntegerField(unique=True)),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name="safeapp",
            name="chains",
            field=models.ManyToManyField(
                related_name="safe_apps", to="safe_apps.chain"
            ),
        ),
        migrations.RunPython(populate_chains, reverse_populate_chains),
    ]
