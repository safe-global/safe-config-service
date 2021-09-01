from django.urls import reverse
from faker import Faker
from rest_framework.test import APITestCase

from chains.tests.factories import ChainFactory, GasPriceFactory


class ChainJsonPayloadFormatViewTests(APITestCase):
    def test_json_payload_format(self):
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
                    "rpcUri": {
                        "authentication": chain.rpc_authentication,
                        "value": chain.rpc_uri,
                    },
                    "safeAppsRpcUri": {
                        "authentication": chain.safe_apps_rpc_authentication,
                        "value": chain.safe_apps_rpc_uri,
                    },
                    "blockExplorerUriTemplate": {
                        "address": chain.block_explorer_uri_address_template,
                        "txHash": chain.block_explorer_uri_tx_hash_template,
                    },
                    "nativeCurrency": {
                        "name": chain.currency_name,
                        "symbol": chain.currency_symbol,
                        "decimals": chain.currency_decimals,
                        "logoUri": chain.currency_logo_uri,
                    },
                    "transactionService": chain.transaction_service_uri,
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
                }
            ],
        }
        url = reverse("v2:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)


class ChainDetailViewTests(APITestCase):
    def test_json_payload_format(self):
        chain = ChainFactory.create(id=1)
        gas_price = GasPriceFactory.create(chain=chain)
        url = reverse("v2:chains:detail", args=[1])
        json_response = {
            "chainId": str(chain.id),
            "chainName": chain.name,
            "rpcUri": {
                "authentication": chain.rpc_authentication,
                "value": chain.rpc_uri,
            },
            "safeAppsRpcUri": {
                "authentication": chain.safe_apps_rpc_authentication,
                "value": chain.safe_apps_rpc_uri,
            },
            "blockExplorerUriTemplate": {
                "address": chain.block_explorer_uri_address_template,
                "txHash": chain.block_explorer_uri_tx_hash_template,
            },
            "nativeCurrency": {
                "name": chain.currency_name,
                "symbol": chain.currency_symbol,
                "decimals": chain.currency_decimals,
                "logoUri": chain.currency_logo_uri,
            },
            "transactionService": chain.transaction_service_uri,
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
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)


class ChainGasPriceViewTests(APITestCase):
    faker = Faker()

    def test_rank_sort(self):
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
                "wei_value": str(gas_price_1.fixed_wei_value),
            },
            {
                "type": "oracle",
                "uri": gas_price_50.oracle_uri,
                "gas_parameter": gas_price_50.oracle_parameter,
                "gwei_factor": str(gas_price_50.gwei_factor),
            },
            {
                "type": "fixed",
                "wei_value": str(gas_price_100.fixed_wei_value),
            },
        ]
        url = reverse("v2:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["gas_price"], expected)

    def test_empty_gas_prices(self):
        ChainFactory.create(id=1)
        url = reverse("v2:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["gas_price"], [])
