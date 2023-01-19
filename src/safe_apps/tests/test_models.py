from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import (
    ClientFactory,
    FeatureFactory,
    ProviderFactory,
    SafeAppFactory,
    SocialProfileFactory,
    TagFactory,
)


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
    def test_allows_create_client_with_valid_domain_name(self) -> None:
        client = ClientFactory.build(url="www.example.com")
        client.full_clean()

    def test_allows_create_client_with_valid_hostname_specifying_protocol(self) -> None:
        client = ClientFactory.build(url="https://www.example.com")
        client.full_clean()

    def test_allows_create_client_with_valid_hostname_with_trailing_slash(self) -> None:
        client = ClientFactory.build(url="https://www.example.com/")
        client.full_clean()

    def test_doesnt_allow_create_client_with_invalid_hostname(self) -> None:
        client = ClientFactory.build(url="https://www.example.com/pump")
        with self.assertRaises(ValidationError):
            client.full_clean()

    def test_doesnt_allow_create_client_with_random_string(self) -> None:
        client = ClientFactory.build(url="random")
        with self.assertRaises(ValidationError):
            client.full_clean()

    def test_str_method_outputs_url(self) -> None:
        client = ClientFactory.create()
        self.assertEqual(str(client), f"Client: {client.url}")


class TagTestCase(TestCase):
    def test_str_method_outputs_tag_name(self) -> None:
        tag = TagFactory.create()
        self.assertEqual(str(tag), f"Tag: {tag.name}")


class FeatureTestCase(TestCase):
    def test_str_method_outputs_feature_key(self) -> None:
        feature = FeatureFactory.create()
        self.assertEqual(str(feature), f"Safe App Feature: {feature.key}")


class SocialProfileTestCase(TestCase):
    def test_str_method_outputs_social_profile_name(self) -> None:
        social_profile = SocialProfileFactory.create()
        self.assertEqual(
            str(social_profile),
            f"Social Profile: {social_profile.platform} | {social_profile.url}",
        )

    def test_doesnt_allow_create_social_profile_with_invalid_url(self) -> None:
        social_profile = SocialProfileFactory.build(url="random")
        with self.assertRaises(ValidationError):
            social_profile.full_clean()

    def test_doesnt_allow_create_social_profile_with_invalid_platform(self) -> None:
        social_profile = SocialProfileFactory.build(platform="bereal")
        with self.assertRaises(ValidationError):
            social_profile.full_clean()

    def test_cannot_exist_without_safe_app(self) -> None:
        social_profile = SocialProfileFactory.build(safe_app=None)
        with self.assertRaises(ValidationError):
            social_profile.full_clean()
