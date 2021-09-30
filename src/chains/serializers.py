from abc import abstractmethod

from drf_yasg.utils import swagger_serializer_method
from gnosis.eth.django.serializers import EthereumAddressField
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import Chain


class GasPriceOracleSerializer(serializers.Serializer):
    type = serializers.ReadOnlyField(default="oracle")
    uri = serializers.URLField(source="oracle_uri")
    gas_parameter = serializers.CharField(source="oracle_parameter")
    gwei_factor = serializers.DecimalField(max_digits=19, decimal_places=9)


class GasPriceFixedSerializer(serializers.Serializer):
    type = serializers.ReadOnlyField(default="fixed")
    wei_value = serializers.CharField(source="fixed_wei_value")


class GasPriceSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if instance.oracle_uri and instance.fixed_wei_value is None:
            return GasPriceOracleSerializer(instance).data
        elif instance.fixed_wei_value and instance.oracle_uri is None:
            return GasPriceFixedSerializer(instance).data
        else:
            raise APIException(
                f"The gas price oracle or a fixed gas price was not provided for chain {instance.chain}"
            )


class ThemeSerializer(serializers.Serializer):
    text_color = serializers.CharField(source="theme_text_color")
    background_color = serializers.CharField(source="theme_background_color")


class CurrencySerializer(serializers.Serializer):
    name = serializers.CharField(source="currency_name")
    symbol = serializers.CharField(source="currency_symbol")
    decimals = serializers.IntegerField(source="currency_decimals")
    logo_uri = serializers.ImageField(use_url=True, source="currency_logo_uri")


class BaseRpcUriSerializer(serializers.Serializer):
    authentication = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    @abstractmethod
    def get_authentication(self, obj):  # pragma: no cover
        pass

    @abstractmethod
    def get_value(self, obj):  # pragma: no cover
        pass


class RpcUriSerializer(BaseRpcUriSerializer):
    def get_authentication(self, obj):
        return obj.rpc_authentication

    def get_value(self, obj):
        return obj.rpc_uri


class SafeAppsRpcUriSerializer(BaseRpcUriSerializer):
    def get_authentication(self, obj):
        return obj.safe_apps_rpc_authentication

    def get_value(self, obj):
        return obj.safe_apps_rpc_uri


class BlockExplorerUriTemplateSerializer(serializers.Serializer):
    address = serializers.URLField(source="block_explorer_uri_address_template")
    tx_hash = serializers.URLField(source="block_explorer_uri_tx_hash_template")


class ChainSerializer(serializers.ModelSerializer):
    chain_id = serializers.CharField(source="id")
    chain_name = serializers.CharField(source="name")
    short_name = serializers.CharField()
    rpc_uri = serializers.SerializerMethodField()
    safe_apps_rpc_uri = serializers.SerializerMethodField()
    block_explorer_uri_template = serializers.SerializerMethodField()
    native_currency = serializers.SerializerMethodField()
    transaction_service = serializers.URLField(
        source="transaction_service_uri", default=None
    )
    vpc_transaction_service = serializers.URLField(source="vpc_transaction_service_uri")
    theme = serializers.SerializerMethodField()
    gas_price = serializers.SerializerMethodField()
    ens_registry_address = EthereumAddressField()

    class Meta:
        model = Chain
        fields = [
            "chain_id",
            "chain_name",
            "short_name",
            "description",
            "l2",
            "rpc_uri",
            "safe_apps_rpc_uri",
            "block_explorer_uri_template",
            "native_currency",
            "transaction_service",
            "vpc_transaction_service",
            "theme",
            "gas_price",
            "ens_registry_address",
            "recommended_master_copy_version",
        ]

    @staticmethod
    @swagger_serializer_method(serializer_or_field=CurrencySerializer)
    def get_native_currency(obj):
        return CurrencySerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=ThemeSerializer)
    def get_theme(obj):
        return ThemeSerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=BaseRpcUriSerializer)
    def get_safe_apps_rpc_uri(obj):
        return SafeAppsRpcUriSerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=BaseRpcUriSerializer)
    def get_rpc_uri(obj):
        return RpcUriSerializer(obj).data

    @staticmethod
    @swagger_serializer_method(serializer_or_field=BlockExplorerUriTemplateSerializer)
    def get_block_explorer_uri_template(obj):
        return BlockExplorerUriTemplateSerializer(obj).data

    @swagger_serializer_method(serializer_or_field=GasPriceSerializer)
    def get_gas_price(self, instance):
        ranked_gas_prices = instance.gasprice_set.all().order_by("rank")
        return GasPriceSerializer(ranked_gas_prices, many=True).data
