import random

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
    rpc_authentication = factory.lazy_attribute(
        lambda o: random.choice(list(Chain.RpcAuthentication))
    )
    rpc_uri = factory.Faker("url")
    safe_apps_rpc_authentication = factory.lazy_attribute(
        lambda o: random.choice(list(Chain.RpcAuthentication))
    )
    safe_apps_rpc_uri = factory.Faker("url")
    block_explorer_uri = factory.Faker("url")
    block_explorer_uri_address_template = factory.Faker("url")
    block_explorer_uri_tx_hash_template = factory.Faker("url")
    currency_name = factory.Faker("cryptocurrency_name")
    currency_symbol = factory.Faker("cryptocurrency_code")
    currency_decimals = factory.Faker("pyint")
    currency_logo_uri = factory.Faker("url")
    transaction_service_uri = factory.Faker("url")
    theme_text_color = factory.Faker("hex_color")
    theme_background_color = factory.Faker("hex_color")
    gas_price_oracle_uri = None
    gas_price_oracle_parameter = None
    ens_registry_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    gas_price_oracle_gwei_factor = factory.Faker(
        "pydecimal", positive=True, min_value=1, max_value=1_000_000_000, right_digits=9
    )
    gas_price_fixed_wei = factory.Faker("pyint")
    recommended_master_copy_version = "1.3.0"
