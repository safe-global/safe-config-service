from django.db import migrations


def copy_chain_ids_to_chains(apps, schema_editor):
    SafeApp = apps.get_model("safe_apps", "SafeApp")
    Chain = apps.get_model("safe_apps", "Chain")

    # Get all SafeApps and their chain_ids
    safe_apps = SafeApp.objects.all()

    # Create Chain objects for any missing chain_ids
    for safe_app in safe_apps:
        for chain_id in safe_app.chain_ids:
            Chain.objects.get_or_create(
                chain_id=chain_id,
                defaults={
                    "name": f"Chain {chain_id}"
                },  # Default name if not already set
            )


def reverse_copy_chain_ids(apps, schema_editor):
    Chain = apps.get_model("safe_apps", "Chain")
    Chain.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("safe_apps", "0015_populate_chains"),
    ]

    operations = [
        migrations.RunPython(copy_chain_ids_to_chains, reverse_copy_chain_ids),
        migrations.RemoveField(
            model_name="safeapp",
            name="chain_ids",
        ),
    ]
