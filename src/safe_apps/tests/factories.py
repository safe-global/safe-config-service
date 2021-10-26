import factory
from factory.django import DjangoModelFactory

from ..models import Provider, SafeApp


class ProviderFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = Provider

    name = factory.Faker("company")
    url = factory.Faker("url")


class SafeAppFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = SafeApp

    app_id = factory.Sequence(lambda id: id)
    visible = True
    url = factory.Faker("url")
    name = factory.Faker("company")
    icon_url = factory.Faker("image_url")
    description = factory.Faker("catch_phrase")
    chain_ids = factory.Faker("pylist", nb_elements=2, value_types=(int,))
    provider = None
