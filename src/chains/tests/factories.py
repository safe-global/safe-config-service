import random

import factory
import web3
from factory.django import DjangoModelFactory

from ..models import Chain, Feature, GasPrice, Wallet


class ChainFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = Chain

    id = factory.Sequence(lambda id: id)
    relevance = factory.Faker("pyint")
    name = factory.Faker("company")
    short_name = factory.Faker("pystr", max_chars=255)
    description = factory.Faker("pystr", max_chars=255)
    chain_logo_uri = factory.django.ImageField(width=50, height=50)
    l2 = factory.Faker("pybool")
    is_testnet = factory.Faker("pybool")
    rpc_authentication = factory.lazy_attribute(
        lambda o: random.choice(list(Chain.RpcAuthentication))
    )
    rpc_uri = factory.Faker("url")
    safe_apps_rpc_authentication = factory.lazy_attribute(
        lambda o: random.choice(list(Chain.RpcAuthentication))
    )
    safe_apps_rpc_uri = factory.Faker("url")
    public_rpc_authentication = factory.lazy_attribute(
        lambda o: random.choice(list(Chain.RpcAuthentication))
    )
    public_rpc_uri = factory.Faker("url")
    block_explorer_uri_address_template = factory.Faker("url")
    block_explorer_uri_tx_hash_template = factory.Faker("url")
    block_explorer_uri_api_template = factory.Faker("url")
    beacon_chain_explorer_uri_public_key_template = factory.Faker("url")
    currency_name = factory.Faker("cryptocurrency_name")
    currency_symbol = factory.Faker("cryptocurrency_code")
    currency_decimals = factory.Faker("pyint")
    currency_logo_uri = factory.django.ImageField(width=50, height=50)
    transaction_service_uri = factory.Faker("url")
    vpc_transaction_service_uri = factory.Faker("url")
    theme_text_color = factory.Faker("hex_color")
    theme_background_color = factory.Faker("hex_color")
    ens_registry_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    recommended_master_copy_version = "1.3.0"
    prices_provider_native_coin = factory.Faker("cryptocurrency_code")
    prices_provider_chain_name = factory.Faker("company")
    balances_provider_chain_name = factory.Faker("company")
    balances_provider_enabled = factory.Faker("pybool")
    hidden = False
    safe_singleton_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    safe_proxy_factory_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    multi_send_address = factory.LazyAttribute(lambda o: web3.Account.create().address)
    multi_send_call_only_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    fallback_handler_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    sign_message_lib_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    create_call_address = factory.LazyAttribute(lambda o: web3.Account.create().address)
    simulate_tx_accessor_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )
    safe_web_authn_signer_factory_address = factory.LazyAttribute(
        lambda o: web3.Account.create().address
    )


class GasPriceFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = GasPrice

    chain = factory.SubFactory(ChainFactory)
    oracle_uri = None
    oracle_parameter = None
    gwei_factor = factory.Faker(
        "pydecimal", positive=True, min_value=1, max_value=1_000_000_000, right_digits=9
    )
    fixed_wei_value = factory.Faker("pyint")
    max_fee_per_gas = None
    max_priority_fee_per_gas = None
    rank = factory.Faker("pyint")


class WalletFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = Wallet

    key = factory.Faker("company")

    @factory.post_generation
    def chains(self, create, extracted, **kwargs):  # type: ignore[no-untyped-def] # decorator is untyped
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of chains were passed in, use them
            for chain in extracted:
                self.chains.add(chain)


class FeatureFactory(DjangoModelFactory):  # type: ignore[misc]
    class Meta:
        model = Feature

    key = factory.Faker("company")

    @factory.post_generation
    def chains(self, create, extracted, **kwargs):  # type: ignore[no-untyped-def] # decorator is untyped
        if not create:
            return

        if extracted:
            for chain in extracted:
                self.chains.add(chain)
