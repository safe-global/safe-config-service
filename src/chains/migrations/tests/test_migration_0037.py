from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations


class Migration0034TestCase(TestMigrations):
    migrate_from = "0036_alter_chain_transaction_service_uri_and_more"
    migrate_to = "0037_chain_hidden"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        Chain = apps.get_model("chains", "Chain")
        Chain.objects.create(
            id=1,
            name="Mainnet",
            short_name="eth",
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
        Chain.objects.create(
            id=100,
            relevance=5,
            name="xDai",
            short_name="xdai",
            description="",
            l2=True,
            rpc_authentication="NO_AUTHENTICATION",
            rpc_uri="https://rpc.xdaichain.com/",
            safe_apps_rpc_authentication="NO_AUTHENTICATION",
            safe_apps_rpc_uri="https://rpc.xdaichain.com/",
            block_explorer_uri_address_template="https://blockscout.com/xdai/mainnet/address/{{address}}/transactions",
            block_explorer_uri_tx_hash_template="https://blockscout.com/xdai/mainnet/tx/{{txHash}}/",
            currency_name="xDai",
            currency_symbol="XDAI",
            currency_decimals=18,
            currency_logo_uri="https://gblobscdn.gitbook.com/",
            transaction_service_uri="http://xdai-safe-transaction-web.safe.svc.cluster.local",
            vpc_transaction_service_uri="",
            theme_text_color="#ffffff",
            theme_background_color="#48A9A6",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )

    def test_chain_accessible(self) -> None:
        Chain = self.apps_registry.get_model("chains", "Chain")

        mainnet = Chain.objects.get(id=1)
        xDai = Chain.objects.get(id=100)

        self.assertEqual(mainnet.hidden, False)
        self.assertEqual(xDai.hidden, False)
