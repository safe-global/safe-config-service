from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations


class Migration0033TestCase(TestMigrations):
    migrate_from = "0032_feature"
    migrate_to = "0033_walletnew"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        WalletOld = apps.get_model("chains", "Wallet")
        WalletOld.objects.create(name="test wallet")

    def test_wallet_migration(self) -> None:
        WalletNew = self.apps_registry.get_model("chains", "Wallet")

        # No exceptions should be risen by get(). If the wallet does not exist DoesNotExist is thrown
        WalletNew.objects.get(key="test wallet")

        self.assertEqual(1, WalletNew.objects.count())
