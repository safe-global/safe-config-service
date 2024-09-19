from typing import Any

from django.db import migrations


def populate_chains(apps: Any, schema_editor: Any) -> None:
    SafeApp = apps.get_model("safe_apps", "SafeApp")
    Chain = apps.get_model("safe_apps", "Chain")

    for safe_app in SafeApp.objects.all():
        for chain_id in safe_app.chain_ids:
            chain, _ = Chain.objects.get_or_create(chain_id=chain_id)
            safe_app.chains.add(chain)


def reverse_populate_chains(apps: Any, schema_editor: Any) -> None:
    SafeApp = apps.get_model("safe_apps", "SafeApp")

    for safe_app in SafeApp.objects.all():
        safe_app.chains.clear()


class Migration(migrations.Migration):

    dependencies = [
        ("safe_apps", "0014_alter_safeapp_icon_url"),
    ]

    operations = [
        migrations.RunPython(populate_chains, reverse_populate_chains),
    ]
