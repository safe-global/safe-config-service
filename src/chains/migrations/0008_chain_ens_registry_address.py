# Generated by Django 3.2.5 on 2021-07-08 11:48

import safe_eth.eth.django.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0007_chain_currency_logo_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="chain",
            name="ens_registry_address",
            field=safe_eth.eth.django.models.EthereumAddressField(
                blank=True, null=True
            ),
        ),
    ]
