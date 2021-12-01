from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations


class Migration0034TestCase(TestMigrations):
    migrate_from = "0033_walletnew"
    migrate_to = "0034_add_public_rpc_url"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        Chain = apps.get_model("chains", "Chain")
        Chain.objects.create(
            id=1,
            name="Mainnet",
            description="",
            l2=False,
            rpc_authentication="API_KEY_PATH",
            rpc_uri="https://mainnet.infura.io/v3/",
            safe_apps_rpc_authentication="API_KEY_PATH",
            safe_apps_rpc_uri="https://mainnet.infura.io/v3/",
            block_explorer_uri_address_template="https://etherscan.io/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://etherscan.io/tx/{{txHash}}",
            currency_name="Ether",
            currency_symbol="ETH",
            currency_decimals=18,
            currency_logo_uri="https://gnosis-safe-token-logos.s3.amazonaws.com/ethereum-eth-logo.png",
            transaction_service_uri="http://mainnet-safe-transaction-web.safe.svc.cluster.local",
            vpc_transaction_service_uri="",
            theme_text_color="#001428",
            theme_background_color="#E8E7E6",
            ens_registry_address="0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e",
            recommended_master_copy_version="1.3.0",
        )

    def test_rpc_copied(self) -> None:
        Chain = self.apps_registry.get_model("chains", "Chain")

        chain = Chain.objects.get(id=1)

        self.assertEqual(chain.rpc_uri, chain.public_rpc_uri)
        self.assertEqual(chain.rpc_authentication, chain.public_rpc_authentication)
