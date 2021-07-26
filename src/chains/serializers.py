from abc import abstractmethod

from drf_yasg.utils import swagger_serializer_method
from gnosis.eth.django.serializers import EthereumAddressField
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import Chain


class GasPriceOracleSerializer(serializers.Serializer):
    type = serializers.ReadOnlyField(default="oracle")
    uri = serializers.URLField(source="gas_price_oracle_uri")
    gas_parameter = serializers.CharField(source="gas_price_oracle_parameter")
    gwei_factor = serializers.DecimalField(
        source="gas_price_oracle_gwei_factor", max_digits=19, decimal_places=9
    )


class GasPriceFixedSerializer(serializers.Serializer):
    type = serializers.ReadOnlyField(default="fixed")
    wei_value = serializers.CharField(source="gas_price_fixed_wei")


class ThemeSerializer(serializers.Serializer):
    text_color = serializers.CharField(source="theme_text_color")
    background_color = serializers.CharField(source="theme_background_color")


class CurrencySerializer(serializers.Serializer):
    name = serializers.CharField(source="currency_name")
    symbol = serializers.CharField(source="currency_symbol")
    decimals = serializers.IntegerField(source="currency_decimals")
    logo_uri = serializers.URLField(source="currency_logo_uri")


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


class ChainSerializer(serializers.ModelSerializer):
    chain_id = serializers.CharField(source="id")
    chain_name = serializers.CharField(source="name")
    rpc_uri = serializers.SerializerMethodField()
    safe_apps_rpc_uri = serializers.SerializerMethodField()
    native_currency = serializers.SerializerMethodField()
    transaction_service = serializers.URLField(
        source="transaction_service_uri", default=None
    )
    theme = serializers.SerializerMethodField()
    gas_price = serializers.SerializerMethodField()
    ens_registry_address = EthereumAddressField()

    class Meta:
        model = Chain
        fields = [
            "chain_id",
            "chain_name",
            "rpc_uri",
            "safe_apps_rpc_uri",
            "block_explorer_uri",
            "native_currency",
            "transaction_service",
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
    def get_gas_price(obj):
        if obj.gas_price_oracle_uri and obj.gas_price_fixed_wei is None:
            return GasPriceOracleSerializer(obj).data
        elif obj.gas_price_fixed_wei and obj.gas_price_oracle_uri is None:
            return GasPriceFixedSerializer(obj).data
        else:
            raise APIException(
                f"The gas price oracle or a fixed gas price was not provided for chain {obj.id}"
            )
