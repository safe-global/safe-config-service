from django.urls import reverse
from rest_framework.test import APITestCase

from .factories import ProviderFactory, SafeAppFactory


class EmptySafeAppsListViewTests(APITestCase):
    def test_empty_set(self):
        url = reverse("safe-apps:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


class JsonPayloadFormatViewTests(APITestCase):
    def test_json_payload_format(self):
        safe_app = SafeAppFactory.create()

        json_response = [
            {
                "url": safe_app.url,
                "name": safe_app.name,
                "iconUrl": safe_app.icon_url,
                "description": safe_app.description,
                "chainIds": safe_app.chain_ids,
                "provider": None,
            }
        ]
        url = reverse("safe-apps:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), json_response)


class FilterSafeAppListViewTests(APITestCase):
    def test_all_safes_returned(self):
        (safe_app_1, safe_app_2, safe_app_3) = SafeAppFactory.create_batch(3)
        json_response = [
            {
                "url": safe_app_1.url,
                "name": safe_app_1.name,
                "icon_url": safe_app_1.icon_url,
                "description": safe_app_1.description,
                "chain_ids": safe_app_1.chain_ids,
                "provider": None,
            },
            {
                "url": safe_app_2.url,
                "name": safe_app_2.name,
                "icon_url": safe_app_2.icon_url,
                "description": safe_app_2.description,
                "chain_ids": safe_app_2.chain_ids,
                "provider": None,
            },
            {
                "url": safe_app_3.url,
                "name": safe_app_3.name,
                "icon_url": safe_app_3.icon_url,
                "description": safe_app_3.description,
                "chain_ids": safe_app_3.chain_ids,
                "provider": None,
            },
        ]
        url = reverse("safe-apps:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)

    def test_all_apps_returned_on_empty_chain_id_value(self):
        (safe_app_1, safe_app_2, safe_app_3) = SafeAppFactory.create_batch(3)
        json_response = [
            {
                "url": safe_app_1.url,
                "name": safe_app_1.name,
                "icon_url": safe_app_1.icon_url,
                "description": safe_app_1.description,
                "chain_ids": safe_app_1.chain_ids,
                "provider": None,
            },
            {
                "url": safe_app_2.url,
                "name": safe_app_2.name,
                "icon_url": safe_app_2.icon_url,
                "description": safe_app_2.description,
                "chain_ids": safe_app_2.chain_ids,
                "provider": None,
            },
            {
                "url": safe_app_3.url,
                "name": safe_app_3.name,
                "icon_url": safe_app_3.icon_url,
                "description": safe_app_3.description,
                "chain_ids": safe_app_3.chain_ids,
                "provider": None,
            },
        ]
        url = reverse("safe-apps:list") + f'{"?chainId="}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)

    def test_apps_returned_on_filtered_chain_id(self):
        SafeAppFactory.create_batch(3, chain_ids=[10])
        (safe_app_4, safe_app_5) = SafeAppFactory.create_batch(2, chain_ids=[1])

        json_response = [
            {
                "url": safe_app_4.url,
                "name": safe_app_4.name,
                "icon_url": safe_app_4.icon_url,
                "description": safe_app_4.description,
                "chain_ids": safe_app_4.chain_ids,
                "provider": None,
            },
            {
                "url": safe_app_5.url,
                "name": safe_app_5.name,
                "icon_url": safe_app_5.icon_url,
                "description": safe_app_5.description,
                "chain_ids": safe_app_5.chain_ids,
                "provider": None,
            },
        ]
        url = reverse("safe-apps:list") + f'{"?chainId=1"}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)

    def test_apps_returned_on_unexisting_chain(self):
        SafeAppFactory.create_batch(3, chain_ids=[12])
        json_response = []
        url = reverse("safe-apps:list") + f'{"?chainId=10"}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)

    def test_apps_returned_on_same_key_pair(self):
        safe_app_1 = SafeAppFactory.create(chain_ids=[1])
        SafeAppFactory.create(chain_ids=[2])
        json_response = [
            {
                "url": safe_app_1.url,
                "name": safe_app_1.name,
                "icon_url": safe_app_1.icon_url,
                "description": safe_app_1.description,
                "chain_ids": safe_app_1.chain_ids,
                "provider": None,
            }
        ]
        url = reverse("safe-apps:list") + f'{"?chainId=2&chainId=1"}'

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)


class ProviderInfoTests(APITestCase):
    def test_provider_returned_in_response(self):
        provider = ProviderFactory.create()
        safe_app = SafeAppFactory.create(provider=provider)

        json_response = [
            {
                "url": safe_app.url,
                "name": safe_app.name,
                "icon_url": safe_app.icon_url,
                "description": safe_app.description,
                "chain_ids": safe_app.chain_ids,
                "provider": {"name": provider.name, "url": provider.url},
            }
        ]
        url = reverse("safe-apps:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)

    def test_provider_not_returned_in_response(self):
        safe_app = SafeAppFactory.create()

        json_response = [
            {
                "url": safe_app.url,
                "name": safe_app.name,
                "icon_url": safe_app.icon_url,
                "description": safe_app.description,
                "chain_ids": safe_app.chain_ids,
                "provider": None,
            }
        ]
        url = reverse("safe-apps:list")

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, json_response)


class CacheSafeAppTests(APITestCase):
    def test_should_cache_response(self):
        safe_app_1 = SafeAppFactory.create()

        json_response = [
            {
                "url": safe_app_1.url,
                "name": safe_app_1.name,
                "icon_url": safe_app_1.icon_url,
                "description": safe_app_1.description,
                "chain_ids": safe_app_1.chain_ids,
                "provider": None,
            }
        ]
        url = reverse("safe-apps:list")

        response = self.client.get(path=url, data=None, format="json")

        cache_control = response.headers.get("Cache-Control")

        self.assertEqual(response.status_code, 200)
        # Cache-Control should be 10 minutes (60 * 10)
        self.assertEqual(cache_control, "max-age=600")
        self.assertEqual(response.data, json_response)
