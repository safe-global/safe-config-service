import factory
from factory.django import DjangoModelFactory

from ..models import Chain


class ChainFactory(DjangoModelFactory):
    class Meta:
        model = Chain

    id = factory.Faker("pyint")
    name = factory.Faker("company")
    rpc_url = factory.Faker("url")
    block_explorer_url = factory.Faker("url")
    currency_name = factory.Faker("cryptocurrency_name")
    currency_symbol = factory.Faker("cryptocurrency_code")
    currency_decimals = factory.Faker("pyint")
