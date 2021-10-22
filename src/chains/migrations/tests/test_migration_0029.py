from django.db.migrations.state import StateApps

from .utils import TestMigrations


class Migration0029TestCase(TestMigrations):
    migrate_from = "0028_chain_vpc_transaction_service_uri"
    migrate_to = "0029_chain_short_name"

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

        Chain.objects.create(
            id=56,
            relevance=15,
            name="Binance Smart Chain",
            description="",
            l2=True,
            rpc_authentication="NO_AUTHENTICATION",
            rpc_uri="https://bsc-dataseed.binance.org/",
            safe_apps_rpc_authentication="NO_AUTHENTICATION",
            safe_apps_rpc_uri="https://bsc-dataseed.binance.org/",
            block_explorer_uri_address_template="https://bscscan.com/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://bscscan.com/tx/{{txHash}}",
            currency_name="BNB",
            currency_symbol="BNB",
            currency_decimals=18,
            currency_logo_uri="https://upload.wikimedia.org/wikipedia/commons/5/57/Binance_Logo.png",
            transaction_service_uri="http://bsc-safe-transaction-web.safe.svc.cluster.local",
            vpc_transaction_service_uri="",
            theme_text_color="#ffffff",
            theme_background_color="#fcc323",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )

        Chain.objects.create(
            id=100,
            relevance=5,
            name="xDai",
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

        Chain.objects.create(
            id=137,
            relevance=10,
            name="Polygon",
            description="",
            l2=True,
            rpc_authentication="API_KEY_PATH",
            rpc_uri="https://polygon-mainnet.infura.io/v3/",
            safe_apps_rpc_authentication="API_KEY_PATH",
            safe_apps_rpc_uri="https://polygon-mainnet.infura.io/v3/",
            block_explorer_uri_address_template="https://polygonscan.com/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://polygonscan.com/tx/{{txHash}}",
            currency_name="Matic",
            currency_symbol="MATIC",
            currency_decimals=18,
            currency_logo_uri="https://cryptologos.cc/logos/polygon-matic-logo.png",
            transaction_service_uri="http://polygon-safe-transaction-web.safe.svc.cluster.local",
            vpc_transaction_service_uri="",
            theme_text_color="#ffffff",
            theme_background_color="#8B50ED",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )

        Chain.objects.create(
            id=246,
            relevance=20,
            name="Energy Web Chain",
            description="",
            l2=True,
            rpc_authentication="NO_AUTHENTICATION",
            rpc_uri="https://rpc.energyweb.org",
            safe_apps_rpc_authentication="NO_AUTHENTICATION",
            safe_apps_rpc_uri="https://rpc.energyweb.org",
            block_explorer_uri_address_template="https://explorer.energyweb.org/address/{{address}}/transactions",
            block_explorer_uri_tx_hash_template="https://explorer.energyweb.org/tx/{{txHash}}/internal-transactions",
            currency_name="Energy Web Token",
            currency_symbol="EWT",
            currency_decimals=18,
            currency_logo_uri="https://cryptologos.cc/logos/energy-web-token-ewt-logo.png?v=013",
            transaction_service_uri="http://ewc-safe-transaction-web.safe.svc.cluster.local",
            vpc_transaction_service_uri="",
            theme_text_color="#ffffff",
            theme_background_color="#A566FF",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )

    def test_short_name_set(self) -> None:
        Chain = self.apps_registry.get_model("chains", "Chain")

        mainnet = Chain.objects.get(id=1)
        binance = Chain.objects.get(id=56)
        x_dai = Chain.objects.get(id=100)
        polygon = Chain.objects.get(id=137)
        ewt = Chain.objects.get(id=246)

        self.assertEqual(mainnet.short_name, "eth")
        self.assertEqual(binance.short_name, "bnb")
        self.assertEqual(x_dai.short_name, "xdai")
        self.assertEqual(polygon.short_name, "matic")
        self.assertEqual(ewt.short_name, "ewt")
