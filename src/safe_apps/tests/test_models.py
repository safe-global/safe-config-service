from django.test import TestCase

from .factories import ProviderFactory, SafeAppFactory


class ProviderTestCase(TestCase):
    def test_str_method_outputs_name_url(self):
        provider = ProviderFactory.create()
        self.assertEqual(str(provider), f"{provider.name} | {provider.url}")


class SafeAppTestCase(TestCase):
    def test_str_method_outputs_name_url_chain_id(self):
        safe_app = SafeAppFactory.create()
        self.assertEqual(
            str(safe_app),
            f"{safe_app.name} | {safe_app.url} | chain_ids={safe_app.chain_ids}",
        )
