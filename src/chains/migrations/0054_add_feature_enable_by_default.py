# SPDX-License-Identifier: FSL-1.1-MIT

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0053_remove_feature_enable_by_default"),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='enable_by_default',
            field=models.BooleanField(default=False, help_text='If checked, this feature will be automatically enabled when creating a chain.'),
        ),
    ]
