from django.urls import reverse
from rest_framework.test import APITestCase

from .factories import ChainFactory


class EmptyChainsListViewTests(APITestCase):
    def test_empty_chains(self):
        url = reverse("chains:list")
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
                    "chainId": chain.id,
                    "chainName": chain.name,
                    "rpcUrl": chain.rpc_url,
                    "blockExplorerUrl": chain.block_explorer_url,
                    "nativeCurrency": {
                        "name": chain.currency_name,
                        "symbol": chain.currency_symbol,
                        "decimals": chain.currency_decimals,
                    },
                }
            ],
        }
        url = reverse("chains:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)


class ChainPaginationViewTests(APITestCase):
    def test_pagination_next_page(self):
        ChainFactory.create_batch(11)
        url = reverse("chains:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        # number of items should be equal to the number of total items
        self.assertEqual(response.json()["count"], 11)
        self.assertEqual(
            response.json()["next"],
            "http://testserver/api/v1/chains/?limit=10&offset=10",
        )
        self.assertEqual(response.json()["previous"], None)
        # returned items should be equal to max_limit
        self.assertEqual(len(response.json()["results"]), 10)

    def test_request_more_than_max_limit_should_return_max_limit(self):
        ChainFactory.create_batch(11)
        # requesting limit > max_limit
        url = reverse("chains:list") + f'{"?limit=11"}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        # number of items should be equal to the number of total items
        self.assertEqual(response.json()["count"], 11)
        self.assertEqual(
            response.json()["next"],
            "http://testserver/api/v1/chains/?limit=10&offset=10",
        )
        self.assertEqual(response.json()["previous"], None)
        # returned items should still be equal to max_limit
        self.assertEqual(len(response.json()["results"]), 10)

    def test_offset_greater_than_count(self):
        ChainFactory.create_batch(11)
        # requesting offset of number of chains
        url = reverse("chains:list") + f'{"?offset=11"}'

        response = self.client.get(path=url, data=None, format="json")

        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 11)
        self.assertEqual(response.json()["next"], None)
        self.assertEqual(
            response.json()["previous"],
            "http://testserver/api/v1/chains/?limit=10&offset=1",
        )
        # returned items should still be zero
        self.assertEqual(len(response.json()["results"]), 0)
