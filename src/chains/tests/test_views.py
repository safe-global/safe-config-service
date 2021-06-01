from django.urls import reverse
from rest_framework.test import APITestCase

from .factories import ChainFactory


class EmptyChainsListViewTests(APITestCase):
    def test_empty_chains(self):
        url = reverse("chains:chains")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


class ChainJsonPayloadFormatViewTests(APITestCase):
    def test_json_payload_format(self):
        chain = ChainFactory.create()
        json_response = [
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
        ]
        url = reverse("chains:chains")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)
