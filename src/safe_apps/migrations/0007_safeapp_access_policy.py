# Generated by Django 3.2.9 on 2021-12-29 21:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("safe_apps", "0006_safeapp_chain_ids_big_int"),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
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
                    "url",
                    models.CharField(
                        help_text="The domain URL client is hosted at",
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^(https?:\\/\\/)?(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{2,256}\\.[a-z]{2,6}\\/?$",
                                code="invalid_hostname",
                                message="Enter a valid hostname (Without a resource path)",
                            )
                        ],
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="safeapp",
            name="exclusive_clients",
            field=models.ManyToManyField(
                blank=True,
                help_text="Clients that are only allowed to use this SafeApp",
                to="safe_apps.Client",
            ),
        ),
    ]
