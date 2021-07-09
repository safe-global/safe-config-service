import factory
import web3
from factory.django import DjangoModelFactory

from ..models import Chain


class ChainFactory(DjangoModelFactory):
    class Meta:
        model = Chain

    id = factory.Sequence(lambda id: id)
    relevance = factory.Faker("pyint")
    name = factory.Faker("company")
    rpc_url = factory.Faker("url")
    block_explorer_url = factory.Faker("url")
    currency_name = factory.Faker("cryptocurrency_name")
    currency_symbol = factory.Faker("cryptocurrency_code")
    currency_decimals = factory.Faker("pyint")
    currency_logo_url = factory.Faker("url")
    transaction_service_url = factory.Faker("url")
    theme_text_color = factory.Faker("hex_color")
    theme_background_color = factory.Faker("hex_color")
    gas_price_oracle_url = factory.Faker("url")
    gas_price_oracle_parameter = factory.Faker(
        "random_element", elements=("safeLow", "average", "fast")
    )
    ens_registry_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    gas_price_oracle_gwei_factor = factory.Faker(
        "pydecimal", positive=True, min_value=1, max_value=1_000_000_000, right_digits=9
    )
