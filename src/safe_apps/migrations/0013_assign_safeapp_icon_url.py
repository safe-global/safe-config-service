# Associated with migration #0014, ensuring that all SafeApps have an icon_url
# before making it non-nullable. Assigning a value and changing the field to
# non-nullable in the same migration otherwise causes an error.

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps
from django.db.models import Q


def assign_missing_default_icon_url(
    apps: StateApps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    SafeApp = apps.get_model("safe_apps", "SafeApp")
    default_icon_url = "safe_apps/icon_url.jpg"

    SafeApp.objects.filter(Q(icon_url__isnull=True) | Q(icon_url="")).update(
        icon_url=default_icon_url
    )


class Migration(migrations.Migration):

    dependencies = [
        ("safe_apps", "0012_rename_visible_safeapp_listed"),
    ]

    operations = [
        migrations.RunPython(
            assign_missing_default_icon_url, reverse_code=migrations.RunPython.noop
        ),
    ]
