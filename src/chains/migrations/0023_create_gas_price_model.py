# Generated by Django 3.2.6 on 2021-09-01 12:38

import django.db.models.deletion
import safe_eth.eth.django.models
from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def copy_gas_prices(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    GasPrice = apps.get_model("chains", "GasPrice")
    Chain = apps.get_model("chains", "Chain")

    GasPrice.objects.bulk_create(
        GasPrice(
            chain=chain,
            oracle_uri=chain.gas_price_oracle_uri,
            oracle_parameter=chain.gas_price_oracle_parameter,
            gwei_factor=chain.gas_price_oracle_gwei_factor,
            fixed_wei_value=chain.gas_price_fixed_wei,
        )
        for chain in Chain.objects.all()
    )


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0022_remove_chain_block_explorer_uri"),
    ]

    operations = [
        migrations.CreateModel(
            name="GasPrice",
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
                ("oracle_uri", models.URLField(blank=True, null=True)),
                (
                    "oracle_parameter",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "gwei_factor",
                    models.DecimalField(
                        decimal_places=9,
                        default=1,
                        help_text="Factor required to reach the Gwei unit",
                        max_digits=19,
                        verbose_name="Gwei multiplier factor",
                    ),
                ),
                (
                    "fixed_wei_value",
                    safe_eth.eth.django.models.Uint256Field(  # type: ignore[no-untyped-call]
                        blank=True, null=True, verbose_name="Fixed gas price (wei)"
                    ),
                ),
                ("rank", models.SmallIntegerField(default=100)),
                (
                    "chain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="chains.chain"
                    ),
                ),
            ],
        ),
        # noop for backwards because it will be handled by the backwards of CreateModel (ie.: destroying the model)
        migrations.RunPython(copy_gas_prices, migrations.RunPython.noop),
    ]
