# Generated by Django 3.2.4 on 2021-06-18 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("safe_apps", "0002_rename_networks_safeapp_chain_ids"),
    ]

    operations = [
        migrations.AlterField(
            model_name="safeapp",
            name="provider",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="safe_apps.provider",
            ),
        ),
    ]
