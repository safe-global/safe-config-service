import json

from django.urls import reverse
from rest_framework.test import APITestCase

from ..models import SafeApp, Provider


class EmptySafeAppsListViewTests(APITestCase):
    def test_empty_set(self):
        url = reverse('v1:safe-apps')

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])


class SingleSafeAppListViewTests(APITestCase):

    def setUp(self) -> None:
        SafeApp.objects.create(
            url="https://example.com",
            name="test_safe_app",
            icon_url="https://example.com/icon",
            description="safe_app_description",
            networks=[1]
        )

    def test_safe_app_returned(self):
        json_response = [{
            'url': 'https://example.com',
            'name': 'test_safe_app',
            'icon_url': 'https://example.com/icon',
            'description': 'safe_app_description',
            'networks': [1],
            'provider': None
        }]
        url = reverse('v1:safe-apps')

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), json_response)


class FilterSafeAppListViewTests(APITestCase):

    def setUp(self) -> None:
        SafeApp.objects.create(
            url="https://example.com/1",
            name="test_safe_app_1",
            icon_url="https://example.com/icon",
            description="safe_app_description_1",
            networks=[1],
            provider=None
        )

        SafeApp.objects.create(
            url="https://example.com/2",
            name="test_safe_app_2",
            icon_url="https://example.com/icon",
            description="safe_app_description_2",
            networks=[1],
            provider=None
        )

        SafeApp.objects.create(
            url="https://example.com/3",
            name="test_safe_app_3",
            icon_url="https://example.com/icon",
            description="safe_app_description_3",
            networks=[2],
            provider=None
        )

    def test_all_safes_returned(self):
        json_response = [
            {
                'url': 'https://example.com/1',
                'name': 'test_safe_app_1',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_1',
                'networks': [1],
                'provider': None
            },
            {
                'url': 'https://example.com/2',
                'name': 'test_safe_app_2',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_2',
                'networks': [1],
                'provider': None
            },
            {
                'url': 'https://example.com/3',
                'name': 'test_safe_app_3',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_3',
                'networks': [2],
                'provider': None
            },
        ]
        url = reverse('v1:safe-apps')

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), json_response)

    def test_all_apps_returned_on_empty_network_value(self):
        json_response = [
            {
                'url': 'https://example.com/1',
                'name': 'test_safe_app_1',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_1',
                'networks': [1],
                'provider': None
            },
            {
                'url': 'https://example.com/2',
                'name': 'test_safe_app_2',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_2',
                'networks': [1],
                'provider': None
            },
            {
                'url': 'https://example.com/3',
                'name': 'test_safe_app_3',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_3',
                'networks': [2],
                'provider': None
            },
        ]
        url = reverse('v1:safe-apps') + f'{"?network_id="}'

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), json_response)

    def test_apps_returned_on_filtered_network(self):
        json_response = [
            {
                'url': 'https://example.com/1',
                'name': 'test_safe_app_1',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_1',
                'networks': [1],
                'provider': None
            },
            {
                'url': 'https://example.com/2',
                'name': 'test_safe_app_2',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_2',
                'networks': [1],
                'provider': None
            }
        ]
        url = reverse('v1:safe-apps') + f'{"?network_id=1"}'

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), json_response)

    def test_apps_returned_on_unexisting_network(self):
        json_response = []
        url = reverse('v1:safe-apps') + f'{"?network_id=10"}'

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), json_response)

    def test_apps_returned_on_same_key_pair(self):
        json_response = [
            {
                'url': 'https://example.com/1',
                'name': 'test_safe_app_1',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_1',
                'networks': [1],
                'provider': None
            },
            {
                'url': 'https://example.com/2',
                'name': 'test_safe_app_2',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_2',
                'networks': [1],
                'provider': None
            }
        ]
        url = reverse('v1:safe-apps') + f'{"?network_id=2&network_id=1"}'

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), json_response)


class ProviderInfoTests(APITestCase):
    def setUp(self) -> None:
        provider = Provider.objects.create(
            url="https://provider1.com",
            name="Provider 1"
        )

        SafeApp.objects.create(
            url="https://example.com/1",
            name="test_safe_app_1",
            icon_url="https://example.com/icon",
            description="safe_app_description_1",
            networks=[1],
            provider=provider
        )

        SafeApp.objects.create(
            url="https://example.com/2",
            name="test_safe_app_2",
            icon_url="https://example.com/icon",
            description="safe_app_description_2",
            networks=[2]
        )

    def test_provider_returned_in_response(self):
        json_response = [
            {
                'url': 'https://example.com/1',
                'name': 'test_safe_app_1',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_1',
                'networks': [1],
                'provider': {
                    'name': 'Provider 1',
                    'url': 'https://provider1.com'
                }
            }
        ]
        url = reverse('v1:safe-apps') + f'{"?network_id=2&network_id=1"}'

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), json_response)

    def test_provider_not_returned_in_response(self):
        json_response = [
            {
                'url': 'https://example.com/2',
                'name': 'test_safe_app_2',
                'icon_url': 'https://example.com/icon',
                'description': 'safe_app_description_2',
                'networks': [2],
                'provider': None,
            }
        ]
        url = reverse('v1:safe-apps') + f'{"?network_id=2&network_id=2"}'

        response = self.client.get(path=url, data=None, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), json_response)
