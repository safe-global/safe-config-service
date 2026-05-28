# SPDX-License-Identifier: FSL-1.1-MIT
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chains", "0054_chain_vpc_rpc_uri"),
    ]

    operations = [
        migrations.AddField(
            model_name="chain",
            name="relayer_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("GTF", "GTF"),
                    ("RELAY_FEE", "Relay Fee"),
                    ("DAILY_LIMIT", "Daily Limit"),
                    ("NO_FEE_CAMPAIGN", "No Fee Campaign"),
                ],
                default=None,
                help_text="Relayer strategy used by the Safe Client Gateway for this chain. Leave empty for no relayer.",
                max_length=32,
                null=True,
            ),
        ),
    ]
