import random

import factory
from factory.django import DjangoModelFactory

from ..models import Client, Feature, Provider, SafeApp, SocialProfile, Tag


class ProviderFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = Provider

    name = factory.Faker("company")
    url = factory.Faker("url")


class ClientFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = Client

    url = factory.Faker("url")


class TagFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = Tag

    name = factory.Faker("word")

    @factory.post_generation
    def safe_apps(self, create, extracted, **kwargs):  # type: ignore[no-untyped-def] # decorator is untyped
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of clients was passed in, use them
            for safe_app in extracted:
                self.safe_apps.add(safe_app)


class SafeAppFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = SafeApp

    app_id = factory.Sequence(lambda id: id)
    listed = True
    url = factory.Faker("url")
    name = factory.Faker("company")
    icon_url = factory.django.ImageField(width=50, height=50)
    description = factory.Faker("catch_phrase")
    chain_ids = factory.Faker("pylist", nb_elements=2, value_types=(int,))
    provider = None
    developer_website = factory.Faker("url")
    featured = factory.Faker("boolean")

    @factory.post_generation
    def exclusive_clients(self, create, extracted, **kwargs):  # type: ignore[no-untyped-def] # decorator is untyped
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of clients was passed in, use them
            for client in extracted:
                self.exclusive_clients.add(client)


class FeatureFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = Feature

    key = factory.Faker("company")

    @factory.post_generation
    def safe_apps(self, create, extracted, **kwargs):  # type: ignore[no-untyped-def] # decorator is untyped
        if not create:
            return

        if extracted:
            for app in extracted:
                self.safe_apps.add(app)


class SocialProfileFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = SocialProfile

    safe_app = factory.SubFactory(SafeAppFactory)
    platform = factory.lazy_attribute(
        lambda o: random.choice(list(SocialProfile.Platform))
    )
    url = factory.Faker("url")

    @factory.post_generation
    def validate(self, create, extracted, **kwargs):  # type: ignore[no-untyped-def] # decorator is untyped
        if not create:
            return
        self.full_clean()
