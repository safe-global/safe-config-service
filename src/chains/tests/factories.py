import random

import factory
import web3
from factory.django import DjangoModelFactory

from ..models import Chain, GasPrice


class ChainFactory(DjangoModelFactory):
    class Meta:
        model = Chain

    id = factory.Sequence(lambda id: id)
    relevance = factory.Faker("pyint")
    name = factory.Faker("company")
    short_name = factory.Faker("pystr", max_chars=255)
    description = factory.Faker("pystr", max_chars=255)
    l2 = factory.Faker("pybool")
    rpc_authentication = factory.lazy_attribute(
        lambda o: random.choice(list(Chain.RpcAuthentication))
    )
    rpc_uri = factory.Faker("url")
    safe_apps_rpc_authentication = factory.lazy_attribute(
        lambda o: random.choice(list(Chain.RpcAuthentication))
    )
    safe_apps_rpc_uri = factory.Faker("url")
    block_explorer_uri_address_template = factory.Faker("url")
    block_explorer_uri_tx_hash_template = factory.Faker("url")
    currency_name = factory.Faker("cryptocurrency_name")
    currency_symbol = factory.Faker("cryptocurrency_code")
    currency_decimals = factory.Faker("pyint")
    currency_logo_uri = factory.django.ImageField()
    transaction_service_uri = factory.Faker("url")
    vpc_transaction_service_uri = factory.Faker("url")
    theme_text_color = factory.Faker("hex_color")
    theme_background_color = factory.Faker("hex_color")
    ens_registry_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    recommended_master_copy_version = "1.3.0"


class GasPriceFactory(DjangoModelFactory):
    class Meta:
        model = GasPrice

    chain = factory.SubFactory(ChainFactory)
    oracle_uri = None
    oracle_parameter = None
    gwei_factor = factory.Faker(
        "pydecimal", positive=True, min_value=1, max_value=1_000_000_000, right_digits=9
    )
    fixed_wei_value = factory.Faker("pyint")
    rank = factory.Faker("pyint")
