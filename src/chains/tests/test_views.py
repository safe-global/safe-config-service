from django.urls import reverse
from faker import Faker
from rest_framework.test import APITestCase

from .factories import ChainFactory


class EmptyChainsListViewTests(APITestCase):
    def test_empty_chains(self):
        url = reverse("v1:chains:list")
        json_response = {"count": 0, "next": None, "previous": None, "results": []}

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)


class ChainJsonPayloadFormatViewTests(APITestCase):
    def test_json_payload_format(self):
        chain = ChainFactory.create()
        json_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "chainId": str(chain.id),
                    "chainName": chain.name,
                    "rpcUri": chain.rpc_uri,
                    "blockExplorerUri": chain.block_explorer_uri,
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
                    "gasPrice": {
                        "type": "fixed",
                        "weiValue": str(chain.gas_price_fixed_wei),
                    },
                    "ensRegistryAddress": chain.ens_registry_address,
                    "recommendedMasterCopyVersion": chain.recommended_master_copy_version,
                }
            ],
        }
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)


class ChainPaginationViewTests(APITestCase):
    def test_pagination_next_page(self):
        ChainFactory.create_batch(11)
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        # number of items should be equal to the number of total items
        self.assertEqual(response.data["count"], 11)
        self.assertEqual(
            response.data["next"],
            "http://testserver/api/v1/chains/?limit=10&offset=10",
        )
        self.assertEqual(response.data["previous"], None)
        # returned items should be equal to max_limit
        self.assertEqual(len(response.data["results"]), 10)

    def test_request_more_than_max_limit_should_return_max_limit(self):
        ChainFactory.create_batch(101)
        # requesting limit > max_limit
        url = reverse("v1:chains:list") + f'{"?limit=101"}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        # number of items should be equal to the number of total items
        self.assertEqual(response.data["count"], 101)
        self.assertEqual(
            response.data["next"],
            "http://testserver/api/v1/chains/?limit=100&offset=100",
        )
        self.assertEqual(response.data["previous"], None)
        # returned items should still be equal to max_limit
        self.assertEqual(len(response.data["results"]), 100)

    def test_offset_greater_than_count(self):
        ChainFactory.create_batch(11)
        # requesting offset of number of chains
        url = reverse("v1:chains:list") + f'{"?offset=11"}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 11)
        self.assertEqual(response.data["next"], None)
        self.assertEqual(
            response.data["previous"],
            "http://testserver/api/v1/chains/?limit=10&offset=1",
        )
        # returned items should still be zero
        self.assertEqual(len(response.data["results"]), 0)


class ChainDetailViewTests(APITestCase):
    def test_json_payload_format(self):
        chain = ChainFactory.create(id=1)
        url = reverse("v1:chains:detail", args=[1])
        json_response = {
            "chainId": str(chain.id),
            "chainName": chain.name,
            "rpcUri": chain.rpc_uri,
            "blockExplorerUri": chain.block_explorer_uri,
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
            "gasPrice": {
                "type": "fixed",
                "weiValue": str(chain.gas_price_fixed_wei),
            },
            "ensRegistryAddress": chain.ens_registry_address,
            "recommendedMasterCopyVersion": chain.recommended_master_copy_version,
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)

    def test_no_match(self):
        ChainFactory.create(id=1)
        url = reverse("v1:chains:detail", args=[2])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 404)

    def test_match(self):
        chain = ChainFactory.create(id=1)
        url = reverse("v1:chains:detail", args=[1])
        json_response = {
            "chain_id": str(chain.id),
            "chain_name": chain.name,
            "rpc_uri": chain.rpc_uri,
            "block_explorer_uri": chain.block_explorer_uri,
            "native_currency": {
                "name": chain.currency_name,
                "symbol": chain.currency_symbol,
                "decimals": chain.currency_decimals,
                "logo_uri": chain.currency_logo_uri,
            },
            "transaction_service": chain.transaction_service_uri,
            "theme": {
                "text_color": chain.theme_text_color,
                "background_color": chain.theme_background_color,
            },
            "gas_price": {
                "type": "fixed",
                "wei_value": str(chain.gas_price_fixed_wei),
            },
            "ens_registry_address": chain.ens_registry_address,
            "recommended_master_copy_version": chain.recommended_master_copy_version,
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)


class ChainsListViewRelevanceTests(APITestCase):
    def test_relevance_sorting(self):
        chain_1 = ChainFactory.create(name="aaa", relevance=10)
        chain_2 = ChainFactory.create(name="bbb", relevance=1)
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        chain_ids = [result["chain_id"] for result in response.data["results"]]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(chain_ids, [str(chain_2.id), str(chain_1.id)])

    def test_same_relevance_sorting(self):
        chain_1 = ChainFactory.create(name="ccc", relevance=10)
        chain_2 = ChainFactory.create(name="bbb", relevance=10)
        chain_3 = ChainFactory.create(name="aaa", relevance=10)
        url = reverse("v1:chains:list")

        response = self.client.get(path=url, data=None, format="json")

        chain_ids = [result["chain_id"] for result in response.data["results"]]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(chain_ids, [str(chain_3.id), str(chain_2.id), str(chain_1.id)])


class ChainsEnsRegistryTests(APITestCase):
    def test_null_ens_registry_address(self):
        ChainFactory.create(id=1, ens_registry_address=None)
        url = reverse("v1:chains:detail", args=[1])

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ens_registry_address"], None)


class ChainGasPriceTests(APITestCase):
    faker = Faker()

    def test_oracle_json_payload_format(self):
        chain = ChainFactory.create(
            id=1, gas_price_oracle_uri=self.faker.url(), gas_price_fixed_wei=None
        )
        url = reverse("v1:chains:detail", args=[1])
        expected_oracle_json_payload = {
            "type": "oracle",
            "uri": chain.gas_price_oracle_uri,
            "gasParameter": chain.gas_price_oracle_parameter,
            "gweiFactor": "{0:.9f}".format(chain.gas_price_oracle_gwei_factor),
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], expected_oracle_json_payload)

    def test_fixed_gas_price_json_payload_format(self):
        chain = ChainFactory.create(id=1, gas_price_fixed_wei=self.faker.pyint())
        url = reverse("v1:chains:detail", args=[1])
        expected_oracle_json_payload = {
            "type": "fixed",
            "weiValue": str(chain.gas_price_fixed_wei),
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], expected_oracle_json_payload)

    def test_oracle_with_fixed(self):
        chain = ChainFactory.create(
            id=1,
            gas_price_oracle_uri=self.faker.url(),
            gas_price_fixed_wei=self.faker.pyint(),
        )
        url = reverse("v1:chains:detail", args=[1])
        expected_error_body = {
            "detail": f"The gas price oracle or a fixed gas price was not provided for chain {chain.id}"
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), expected_error_body)

    def test_fixed_gas_256_bit(self):
        ChainFactory.create(
            id=1,
            gas_price_fixed_wei="115792089237316195423570985008687907853269984665640564039457584007913129639935",
        )
        url = reverse("v1:chains:detail", args=[1])
        expected_oracle_json_payload = {
            "type": "fixed",
            "weiValue": "115792089237316195423570985008687907853269984665640564039457584007913129639935",
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["gasPrice"], expected_oracle_json_payload)
