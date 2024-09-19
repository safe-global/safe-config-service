from typing import Any

from django.db import migrations


def migrate_chain_ids_to_chains(apps: Any, schema_editor: Any) -> None:
    SafeApp = apps.get_model("safe_apps", "SafeApp")
    Chain = apps.get_model("safe_apps", "Chain")

    for safe_app in SafeApp.objects.all():
        chain_ids = safe_app.chain_ids
        for chain_id in chain_ids:
            chain, _ = Chain.objects.get_or_create(chain_id=chain_id)
            safe_app.chains.add(chain)


def reverse_migrate_chain_ids_to_chains(apps: Any, schema_editor: Any) -> None:
    SafeApp = apps.get_model("safe_apps", "SafeApp")

    for safe_app in SafeApp.objects.all():
        safe_app.chain_ids = list(safe_app.chains.values_list("chain_id", flat=True))
        safe_app.save()


class Migration(migrations.Migration):
    dependencies = [
        ("safe_apps", "0015_populate_chains"),
    ]

    operations = [
        migrations.RunPython(
            migrate_chain_ids_to_chains, reverse_migrate_chain_ids_to_chains
        ),
    ]
