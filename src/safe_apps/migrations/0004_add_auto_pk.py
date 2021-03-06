# Generated by Django 3.2.4 on 2021-06-28 14:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("safe_apps", "0003_alter_safeapp_provider"),
    ]

    operations = [
        # Remove Primary Key constraint from safeapp.url
        migrations.AlterField(
            model_name="safeapp",
            name="url",
            field=models.URLField(),
        ),
        # Add safeapp.app_id as primary key
        migrations.AddField(
            model_name="safeapp",
            name="app_id",
            field=models.BigAutoField(primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
