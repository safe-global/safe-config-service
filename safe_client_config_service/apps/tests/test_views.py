import json

from django.urls import reverse
from rest_framework.test import APITestCase

from ..models import SafeApp


class SafeAppsListViewTests(APITestCase):
    def test_empty_set(self):
        url = reverse('v1:safe-apps')
        response = self.client.get(path=url, data=None, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SafeApp.objects.count(), 0)
        self.assertEqual(json.loads(response.content), [])
