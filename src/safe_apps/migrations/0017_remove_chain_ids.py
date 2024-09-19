from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('safe_apps', '0016_chain_ids_to_chains'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='safeapp',
            name='chain_ids',
        ),
    ]