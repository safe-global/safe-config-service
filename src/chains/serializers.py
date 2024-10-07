from abc import abstractmethod
from typing import Any

from drf_yasg.utils import swagger_serializer_method
from gnosis.eth.django.serializers import EthereumAddressField
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.utils.serializer_helpers import ReturnDict

from .models import Chain, Feature, GasPrice, Wallet


class GasPriceOracleSerializer(serializers.Serializer[GasPrice]):
    type = serializers.ReadOnlyField(default="oracle")
    uri = serializers.URLField(source="oracle_uri")
    gas_parameter = serializers.CharField(source="oracle_parameter")
    gwei_factor = serializers.DecimalField(max_digits=19, decimal_places=9)


class GasPriceFixedSerializer(serializers.Serializer[GasPrice]):
    type = serializers.ReadOnlyField(default="fixed")
    wei_value = serializers.CharField(source="fixed_wei_value")


class GasPriceFixed1559Serializer(serializers.Serializer[GasPrice]):
    type = serializers.ReadOnlyField(default="fixed1559")
    max_fee_per_gas = serializers.CharField()
    max_priority_fee_per_gas = serializers.CharField()


class GasPriceSerializer(serializers.ModelSerializer[GasPrice]):
    class Meta:
        fields = [
            "oracle_uri",
            "oracle_parameter",
            "gwei_factor",
            "fixed_wei_value",
            "max_fee_per_gas",
            "max_priority_fee_per_gas",
        ]
        model = GasPrice
        ref_name = "chains.serializers.GasPriceSerializer"

    def to_representation(self, instance: GasPrice) -> ReturnDict[Any, Any]:
        if (
            instance.oracle_uri
            and instance.fixed_wei_value is None
            and instance.max_fee_per_gas is None
            and instance.max_priority_fee_per_gas is None
        ):
            return GasPriceOracleSerializer(instance).data
        elif (
            instance.fixed_wei_value is not None
            and instance.oracle_uri is None
            and instance.max_fee_per_gas is None
            and instance.max_priority_fee_per_gas is None
        ):
            return GasPriceFixedSerializer(instance).data
        elif (
            instance.max_fee_per_gas
            and instance.max_priority_fee_per_gas
            and instance.oracle_uri is None
            and instance.fixed_wei_value is None
        ):
            return GasPriceFixed1559Serializer(instance).data
        else:
            raise APIException(
                f"The gas price oracle or a fixed gas price was not provided for chain {instance.chain}"
            )


class ThemeSerializer(serializers.Serializer[Chain]):
    text_color = serializers.CharField(source="theme_text_color")
    background_color = serializers.CharField(source="theme_background_color")


class CurrencySerializer(serializers.Serializer[Chain]):
    name = serializers.CharField(source="currency_name")
    symbol = serializers.CharField(source="currency_symbol")
    decimals = serializers.IntegerField(source="currency_decimals")
    logo_uri = serializers.ImageField(use_url=True, source="currency_logo_uri")


class PricesProviderSerializer(serializers.Serializer[Chain]):
    native_coin = serializers.CharField(source="prices_provider_native_coin")
    chain_name = serializers.CharField(source="prices_provider_chain_name")


class BalancesProviderSerializer(serializers.Serializer[Chain]):
    chain_name = serializers.CharField(source="balances_provider_chain_name")
    enabled = serializers.BooleanField(source="balances_provider_enabled")


class ContractAddressesSerializer(serializers.Serializer[Chain]):
    safe_singleton_address = serializers.CharField()
    safe_proxy_factory_address = serializers.CharField()
    multi_send_address = serializers.CharField()
    multi_send_call_only_address = serializers.CharField()
    fallback_handler_address = serializers.CharField()
    sign_message_lib_address = serializers.CharField()
    create_call_address = serializers.CharField()
    simulate_tx_accessor_address = serializers.CharField()
    safe_web_authn_signer_factory_address = serializers.CharField()


class BaseRpcUriSerializer(serializers.Serializer[Chain]):
    authentication = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField(method_name="get_rpc_value")

    @abstractmethod
    def get_authentication(self, obj: Chain) -> str:  # pragma: no cover
        pass

    @abstractmethod
    def get_rpc_value(self, obj: Chain) -> str:  # pragma: no cover
        pass


class RpcUriSerializer(BaseRpcUriSerializer):
    def get_authentication(self, obj: Chain) -> str:
        return obj.rpc_authentication

    def get_rpc_value(self, obj: Chain) -> str:
        return obj.rpc_uri


class SafeAppsRpcUriSerializer(BaseRpcUriSerializer):
    def get_authentication(self, obj: Chain) -> str:
        return obj.safe_apps_rpc_authentication

    def get_rpc_value(self, obj: Chain) -> str:
        return obj.safe_apps_rpc_uri


class PublicRpcUriSerializer(BaseRpcUriSerializer):
    def get_authentication(self, obj: Chain) -> str:
        return obj.public_rpc_authentication

    def get_rpc_value(self, obj: Chain) -> str:
        return obj.public_rpc_uri


class BlockExplorerUriTemplateSerializer(serializers.Serializer[Chain]):
    address = serializers.URLField(source="block_explorer_uri_address_template")
    tx_hash = serializers.URLField(source="block_explorer_uri_tx_hash_template")
    api = serializers.URLField(source="block_explorer_uri_api_template")


class BeaconChainExplorerUriTemplateSerializer(serializers.Serializer[Chain]):
    public_key = serializers.URLField(
        source="beacon_chain_explorer_uri_public_key_template"
    )


class FeatureSerializer(serializers.ModelSerializer[Feature]):
    class Meta:
        fields = ["key"]
        model = Feature
        ref_name = "chains.serializers.FeatureSerializer"

    @staticmethod
    def to_representation(instance: Feature) -> str:  # type: ignore[override]
        return instance.key


class WalletSerializer(serializers.ModelSerializer[Wallet]):
    class Meta:
        fields = ["key"]
        model = Wallet
        ref_name = "chains.serializers.WalletSerializer"

    @staticmethod
    def to_representation(instance: Wallet) -> str:  # type: ignore[override]
        return instance.key


class ChainSerializer(serializers.ModelSerializer[Chain]):
    chain_id = serializers.CharField(source="id")
    chain_name = serializers.CharField(source="name")
    short_name = serializers.CharField()
    chain_logo_uri = serializers.ImageField(use_url=True)
    rpc_uri = serializers.SerializerMethodField()
    safe_apps_rpc_uri = serializers.SerializerMethodField()
    public_rpc_uri = serializers.SerializerMethodField()
    block_explorer_uri_template = serializers.SerializerMethodField()
    beacon_chain_explorer_uri_template = serializers.SerializerMethodField()
    native_currency = serializers.SerializerMethodField()
    prices_provider = serializers.SerializerMethodField()
    contract_addresses = serializers.SerializerMethodField()
    balances_provider = serializers.SerializerMethodField()
    transaction_service = serializers.URLField(
        source="transaction_service_uri", default=None
    )
    vpc_transaction_service = serializers.URLField(source="vpc_transaction_service_uri")
    theme = serializers.SerializerMethodField()
    gas_price = serializers.SerializerMethodField()
    ens_registry_address = EthereumAddressField()
    disabled_wallets = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = Chain
        fields = [
            "chain_id",
            "chain_name",
            "short_name",
            "description",
            "chain_logo_uri",
            "l2",
            "is_testnet",
            "rpc_uri",
            "safe_apps_rpc_uri",
            "public_rpc_uri",
            "block_explorer_uri_template",
            "beacon_chain_explorer_uri_template",
            "native_currency",
            "prices_provider",
            "balances_provider",
            "contract_addresses",
            "transaction_service",
            "vpc_transaction_service",
            "theme",
            "gas_price",
            "ens_registry_address",
            "recommended_master_copy_version",
            "disabled_wallets",
            "features",
        ]

    @swagger_serializer_method(serializer_or_field=CurrencySerializer)  # type: ignore[misc]
    def get_native_currency(self, obj: Chain) -> ReturnDict[Any, Any]:
        return CurrencySerializer(
            obj, context={"request": self.context["request"]}
        ).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=ThemeSerializer)  # type: ignore[misc]
    def get_theme(obj: Chain) -> ReturnDict[Any, Any]:
        return ThemeSerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=BaseRpcUriSerializer)  # type: ignore[misc]
    def get_safe_apps_rpc_uri(obj: Chain) -> ReturnDict[Any, Any]:
        return SafeAppsRpcUriSerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=BaseRpcUriSerializer)  # type: ignore[misc]
    def get_rpc_uri(obj: Chain) -> ReturnDict[Any, Any]:
        return RpcUriSerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=BaseRpcUriSerializer)  # type: ignore[misc]
    def get_public_rpc_uri(obj: Chain) -> ReturnDict[Any, Any]:
        return PublicRpcUriSerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=BlockExplorerUriTemplateSerializer)  # type: ignore[misc]
    def get_block_explorer_uri_template(obj: Chain) -> ReturnDict[Any, Any]:
        return BlockExplorerUriTemplateSerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=BeaconChainExplorerUriTemplateSerializer)  # type: ignore[misc]
    def get_beacon_chain_explorer_uri_template(obj: Chain) -> ReturnDict[Any, Any]:
        return BeaconChainExplorerUriTemplateSerializer(obj).data

    @swagger_serializer_method(serializer_or_field=GasPriceSerializer)  # type: ignore[misc]
    def get_gas_price(self, instance: Chain) -> ReturnDict[Any, Any]:
        ranked_gas_prices = instance.gasprice_set.all().order_by("rank")
        return GasPriceSerializer(ranked_gas_prices, many=True).data

    @swagger_serializer_method(serializer_or_field=WalletSerializer)  # type: ignore[misc]
    def get_disabled_wallets(self, instance: Chain) -> ReturnDict[Any, Any]:
        disabled_wallets = instance.get_disabled_wallets().order_by("key")
        return WalletSerializer(disabled_wallets, many=True).data

    @swagger_serializer_method(serializer_or_field=FeatureSerializer)  # type: ignore[misc]
    def get_features(self, instance: Chain) -> ReturnDict[Any, Any]:
        enabled_features = instance.feature_set.all().order_by("key")
        return FeatureSerializer(enabled_features, many=True).data

    @swagger_serializer_method(serializer_or_field=PricesProviderSerializer)  # type: ignore[misc]
    def get_prices_provider(self, instance: Chain) -> ReturnDict[Any, Any]:
        return PricesProviderSerializer(instance).data

    @swagger_serializer_method(serializer_or_field=BalancesProviderSerializer)  # type: ignore[misc]
    def get_balances_provider(self, instance: Chain) -> ReturnDict[Any, Any]:
        return BalancesProviderSerializer(instance).data

    @swagger_serializer_method(serializer_or_field=ContractAddressesSerializer)  # type: ignore[misc]
    def get_contract_addresses(self, instance: Chain) -> ReturnDict[Any, Any]:
        return ContractAddressesSerializer(instance).data
