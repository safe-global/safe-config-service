from django.test import TestCase

from .factories import ClientFactory, ProviderFactory, SafeAppFactory


class ProviderTestCase(TestCase):
    def test_str_method_outputs_name_url(self) -> None:
        provider = ProviderFactory.create()
        self.assertEqual(str(provider), f"{provider.name} | {provider.url}")


class SafeAppTestCase(TestCase):
    def test_str_method_outputs_name_url_chain_id(self) -> None:
        safe_app = SafeAppFactory.create()
        self.assertEqual(
            str(safe_app),
            f"{safe_app.name} | {safe_app.url} | chain_ids={safe_app.chain_ids}",
        )

    @staticmethod
    def test_empty_provider_validation() -> None:
        safe_app = SafeAppFactory.create(provider=None)

        # Run validations including blank checks
        safe_app.full_clean()


class ClientTestCase(TestCase):
    def test_str_method_outputs_url(self) -> None:
        client = ClientFactory.create()
        self.assertEqual(str(client), f"Client: {client.url}")
