from decimal import Decimal
from typing import Any

from django.urls import reverse
from faker import Faker
from rest_framework.test import APITestCase

from .factories import ChainFactory, FeatureFactory, GasPriceFactory, WalletFactory


class EmptyChainsListViewTests(APITestCase):
    def test_empty_chains(self) -> None:
        url = reverse("v1:chains:list")
        json_response: dict[str, Any] = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)


class ChainJsonPayloadFormatViewTests(APITestCase):
    def test_json_payload_format(self) -> None:
        chain = ChainFactory.create()
        gas_price = GasPriceFactory.create(chain=chain)
        json_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "chainId": str(gas_price.chain.id),
                    "chainName": chain.name,
                    "shortName": chain.short_name,
                    "description": chain.description,
                    # Absolute URL because chain_logo_uri is defined at top level and BASE_DIR
                    # is folder structure dependent, see currency_logo_uri for relative URL
                    "chainLogoUri": f"http://testserver{chain.chain_logo_uri.url}",
                    "l2": chain.l2,
                    "isTestnet": chain.is_testnet,
                    "rpcUri": {
                        "authentication": chain.rpc_authentication,
                        "value": chain.rpc_uri,
                    },
                    "safeAppsRpcUri": {
                        "authentication": chain.safe_apps_rpc_authentication,
                        "value": chain.safe_apps_rpc_uri,
                    },
                    "publicRpcUri": {
                        "authentication": chain.public_rpc_authentication,
                        "value": chain.public_rpc_uri,
                    },
                    "blockExplorerUriTemplate": {
                        "address": chain.block_explorer_uri_address_template,
                        "txHash": chain.block_explorer_uri_tx_hash_template,
                        "api": chain.block_explorer_uri_api_template,
                    },
                    "nativeCurrency": {
                        "name": chain.currency_name,
                        "symbol": chain.currency_symbol,
                        "decimals": chain.currency_decimals,
                        "logoUri": f"http://testserver{chain.currency_logo_uri.url}",
                    },
                    "pricesProvider": {
                        "nativeCoin": chain.prices_provider_native_coin,
                        "chainName": chain.prices_provider_chain_name,
                    },
                    "balancesProvider": {
                        "chainName": chain.balances_provider_chain_name,
                        "enabled": chain.balances_provider_enabled,
                    },
                    "transactionService": chain.transaction_service_uri,
                    "vpcTransactionService": chain.vpc_transaction_service_uri,
                    "theme": {
                        "textColor": chain.theme_text_color,
                        "backgroundColor": chain.theme_background_color,
                    },
                    "gasPrice": [
                        {
                            "type": "fixed",
                            "weiValue": str(gas_price.fixed_wei_value),
                        }
                    ],
                    "ensRegistryAddress": chain.ens_registry_address,
                    "recommendedMasterCopyVersion": chain.recommended_master_copy_version,
                    "disabledWallets": [],
                    "features": [],
                }
            ],
        }
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)


class ChainPaginationViewTests(APITestCase):
    def test_pagination_next_page(self) -> None:
        ChainFactory.create_batch(21)
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        # number of items should be equal to the number of total items
        self.assertEqual(response.json()["count"], 21)
        self.assertEqual(
            response.json()["next"],
            "http://testserver/api/v1/chains/?limit=20&offset=20",
        )
        self.assertEqual(response.json()["previous"], None)
        # returned items should be equal to max_limit
        self.assertEqual(len(response.json()["results"]), 20)

    def test_request_more_than_max_limit_should_return_max_limit(self) -> None:
        ChainFactory.create_batch(101)
        # requesting limit > max_limit
        url = reverse("v1:chains:list") + f'{"?limit=101"}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        # number of items should be equal to the number of total items
        self.assertEqual(response.json()["count"], 101)
        self.assertEqual(
            response.json()["next"],
            "http://testserver/api/v1/chains/?limit=20&offset=20",
        )
        self.assertEqual(response.json()["previous"], None)
        # returned items should still be equal to max_limit
        self.assertEqual(len(response.json()["results"]), 20)

    def test_offset_greater_than_count(self) -> None:
        ChainFactory.create_batch(21)
        # requesting offset of number of chains
        url = reverse("v1:chains:list") + f'{"?offset=21"}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 21)
        self.assertEqual(response.json()["next"], None)
        self.assertEqual(
            response.json()["previous"],
            "http://testserver/api/v1/chains/?limit=20&offset=1",
        )
        # returned items should still be zero
        self.assertEqual(len(response.json()["results"]), 0)


class ChainDetailViewTests(APITestCase):
    def test_json_payload_format(self) -> None:
        chain = ChainFactory.create(id=1)
        gas_price = GasPriceFactory.create(chain=chain)
        url = reverse("v1:chains:detail", args=[1])
        json_response = {
            "chainId": str(chain.id),
            "chainName": chain.name,
            "shortName": chain.short_name,
            "description": chain.description,
            # Absolute URL because chain_logo_uri is defined at top level and BASE_DIR
            # is folder structure dependent, see currency_logo_uri for relative URL
            "chainLogoUri": f"http://testserver{chain.chain_logo_uri.url}",
            "l2": chain.l2,
            "isTestnet": chain.is_testnet,
            "rpcUri": {
                "authentication": chain.rpc_authentication,
                "value": chain.rpc_uri,
            },
            "safeAppsRpcUri": {
                "authentication": chain.safe_apps_rpc_authentication,
                "value": chain.safe_apps_rpc_uri,
            },
            "publicRpcUri": {
                "authentication": chain.public_rpc_authentication,
                "value": chain.public_rpc_uri,
            },
            "blockExplorerUriTemplate": {
                "address": chain.block_explorer_uri_address_template,
                "txHash": chain.block_explorer_uri_tx_hash_template,
                "api": chain.block_explorer_uri_api_template,
            },
            "nativeCurrency": {
                "name": chain.currency_name,
                "symbol": chain.currency_symbol,
                "decimals": chain.currency_decimals,
                "logoUri": f"http://testserver{chain.currency_logo_uri.url}",
            },
            "pricesProvider": {
                "nativeCoin": chain.prices_provider_native_coin,
                "chainName": chain.prices_provider_chain_name,
            },
            "balancesProvider": {
                "chainName": chain.balances_provider_chain_name,
                "enabled": chain.balances_provider_enabled,
            },
            "transactionService": chain.transaction_service_uri,
            "vpcTransactionService": chain.vpc_transaction_service_uri,
            "theme": {
                "textColor": chain.theme_text_color,
                "backgroundColor": chain.theme_background_color,
            },
            "gasPrice": [
                {
                    "type": "fixed",
                    "weiValue": str(gas_price.fixed_wei_value),
                }
            ],
            "ensRegistryAddress": chain.ens_registry_address,
            "recommendedMasterCopyVersion": chain.recommended_master_copy_version,
            "disabledWallets": [],
            "features": [],
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)

    def test_no_match(self) -> None:
        ChainFactory.create(id=1)
        url = reverse("v1:chains:detail", args=[2])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 404)

    def test_hidden_chain_no_match(self) -> None:
        ChainFactory.create(id=1, hidden=True)
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 404)

    def test_by_short_name(self) -> None:
        ChainFactory.create(id=1, short_name="eth")
        url_by_id = reverse("v1:chains:detail", args=[1])
        url_by_short_name = reverse("v1:chains:detail_by_short_name", args=["eth"])

        response_by_id = self.client.get(path=url_by_id, data=None, format="json")
        response_by_short_name = self.client.get(
            path=url_by_short_name, data=None, format="json"
        )

        self.assertEqual(response_by_id.status_code, 200)
        self.assertEqual(response_by_short_name.status_code, 200)
        self.assertEqual(response_by_id.json(), response_by_short_name.json())

    def test_hidden_chain_by_short_name_no_match(self) -> None:
        ChainFactory.create(id=1, short_name="eth", hidden=True)
        url_by_short_name = reverse("v1:chains:detail_by_short_name", args=["eth"])

        response_by_short_name = self.client.get(
            path=url_by_short_name, data=None, format="json"
        )

        self.assertEqual(response_by_short_name.status_code, 404)


class ChainsListViewRelevanceTests(APITestCase):
    def test_relevance_sorting(self) -> None:
        chain_1 = ChainFactory.create(name="aaa", relevance=10)
        chain_2 = ChainFactory.create(name="bbb", relevance=1)
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        chain_ids = [result["chainId"] for result in response.json()["results"]]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(chain_ids, [str(chain_2.id), str(chain_1.id)])

    def test_same_relevance_sorting(self) -> None:
        chain_1 = ChainFactory.create(name="ccc", relevance=10)
        chain_2 = ChainFactory.create(name="bbb", relevance=10)
        chain_3 = ChainFactory.create(name="aaa", relevance=10)
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        chain_ids = [result["chainId"] for result in response.json()["results"]]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(chain_ids, [str(chain_3.id), str(chain_2.id), str(chain_1.id)])


class ChainsListViewHiddenTests(APITestCase):
    def test_hidden_chains_get_ignored(self) -> None:
        ChainFactory.create_batch(5)
        ChainFactory.create(hidden=True)
        ChainFactory.create(hidden=True)
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 5)
        self.assertEqual(len(response.json()["results"]), 5)


class ChainsEnsRegistryTests(APITestCase):
    def test_null_ens_registry_address(self) -> None:
        ChainFactory.create(id=1, ens_registry_address=None)
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ensRegistryAddress"], None)


class ChainGasPriceTests(APITestCase):
    faker = Faker()

    def test_rank_sort(self) -> None:
        chain = ChainFactory.create(id=1)
        # fixed price rank 100
        gas_price_100 = GasPriceFactory.create(
            chain=chain,
            rank=100,
        )
        # oracle price rank 50
        gas_price_50 = GasPriceFactory.create(
            chain=chain,
            oracle_uri=self.faker.url(),
            oracle_parameter="fast",
            fixed_wei_value=None,
            rank=50,
        )
        # fixed price rank 1
        gas_price_1 = GasPriceFactory.create(
            chain=chain,
            rank=1,
        )
        expected = [
            {
                "type": "fixed",
                "weiValue": str(gas_price_1.fixed_wei_value),
            },
            {
                "type": "oracle",
                "uri": gas_price_50.oracle_uri,
                "gasParameter": gas_price_50.oracle_parameter,
                "gweiFactor": str(
                    gas_price_50.gwei_factor.quantize(Decimal("1.000000000"))
                ),
            },
            {
                "type": "fixed",
                "weiValue": str(gas_price_100.fixed_wei_value),
            },
        ]
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], expected)

    def test_empty_gas_prices(self) -> None:
        ChainFactory.create(id=1)
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], [])

    def test_oracle_json_payload_format(self) -> None:
        chain = ChainFactory.create(id=1)
        gas_price = GasPriceFactory.create(
            chain=chain, oracle_uri=self.faker.url(), fixed_wei_value=None
        )
        url = reverse("v1:chains:detail", args=[1])
        expected_oracle_json_payload = [
            {
                "type": "oracle",
                "uri": gas_price.oracle_uri,
                "gasParameter": gas_price.oracle_parameter,
                "gweiFactor": "{0:.9f}".format(gas_price.gwei_factor),
            }
        ]

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], expected_oracle_json_payload)

    def test_fixed_gas_price_json_payload_format(self) -> None:
        chain = ChainFactory.create(id=1)
        gas_price = GasPriceFactory.create(
            chain=chain, fixed_wei_value=self.faker.pyint()
        )
        url = reverse("v1:chains:detail", args=[1])
        expected_oracle_json_payload = [
            {
                "type": "fixed",
                "weiValue": str(gas_price.fixed_wei_value),
            }
        ]

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], expected_oracle_json_payload)

    def test_oracle_with_fixed(self) -> None:
        chain = ChainFactory.create(id=1)
        GasPriceFactory.create(
            chain=chain,
            oracle_uri=self.faker.url(),
            fixed_wei_value=self.faker.pyint(),
        )
        url = reverse("v1:chains:detail", args=[1])
        expected_error_body = {
            "detail": f"The gas price oracle or a fixed gas price was not provided for chain {chain}"
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), expected_error_body)

    def test_fixed_gas_256_bit(self) -> None:
        chain = ChainFactory.create(id=1)
        GasPriceFactory.create(
            chain=chain,
            fixed_wei_value="115792089237316195423570985008687907853269984665640564039457584007913129639935",
        )
        url = reverse("v1:chains:detail", args=[1])
        expected_oracle_json_payload = [
            {
                "type": "fixed",
                "weiValue": "115792089237316195423570985008687907853269984665640564039457584007913129639935",
            }
        ]

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], expected_oracle_json_payload)

    def test_fixed_gas_price_1559_json_payload_format(self) -> None:
        chain = ChainFactory.create(id=1)
        gas_price = GasPriceFactory.create(
            chain=chain,
            max_fee_per_gas=self.faker.pyint(),
            max_priority_fee_per_gas=self.faker.pyint(),
            fixed_wei_value=None,
        )
        url = reverse("v1:chains:detail", args=[1])
        expected_oracle_json_payload = [
            {
                "type": "fixed1559",
                "maxFeePerGas": str(gas_price.max_fee_per_gas),
                "maxPriorityFeePerGas": str(gas_price.max_priority_fee_per_gas),
            }
        ]

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], expected_oracle_json_payload)


class WalletTests(APITestCase):
    def test_wallet_with_no_chains_show_as_disabled(self) -> None:
        ChainFactory.create(id=1)
        wallet = WalletFactory.create(chains=())
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["disabledWallets"], [wallet.key])

    def test_multiple_disabled_wallets_name_sorting(self) -> None:
        ChainFactory.create(id=1)
        wallet_1 = WalletFactory.create(key="zWallet", chains=())
        wallet_2 = WalletFactory.create(key="gWallet", chains=())
        wallet_3 = WalletFactory.create(key="aWallet", chains=())
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["disabledWallets"],
            [wallet_3.key, wallet_2.key, wallet_1.key],
        )

    def test_wallet_with_chains_does_not_show(self) -> None:
        chain = ChainFactory.create(id=1)
        WalletFactory.create(chains=(chain,))
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["disabledWallets"], [])


class FeatureTests(APITestCase):
    def test_feature_disabled_for_chain(self) -> None:
        ChainFactory.create(id=1)
        feature = FeatureFactory.create(chains=())
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(feature.key not in response.json()["features"])

    def test_feature_enabled_for_chain(self) -> None:
        chain = ChainFactory.create(id=1)
        feature = FeatureFactory.create(chains=(chain,))
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(feature.key in response.json()["features"])

    def test__multiple_features_sorting(self) -> None:
        chain = ChainFactory.create(id=1)
        feature_1 = FeatureFactory.create(key="zFeature", chains=(chain,))
        feature_2 = FeatureFactory.create(key="gFeature", chains=(chain,))
        feature_3 = FeatureFactory.create(key="aFeature", chains=(chain,))
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["features"],
            [feature_3.key, feature_2.key, feature_1.key],
        )
