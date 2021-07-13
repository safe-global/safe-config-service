from drf_yasg.utils import swagger_serializer_method
from gnosis.eth.django.serializers import EthereumAddressField
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import Chain


class GasPriceOracleSerializer(serializers.Serializer):
    type = serializers.ReadOnlyField(default="oracle")
    url = serializers.URLField(source="gas_price_oracle_url")
    gas_parameter = serializers.CharField(source="gas_price_oracle_parameter")
    gwei_factor = serializers.DecimalField(
        source="gas_price_oracle_gwei_factor", max_digits=19, decimal_places=9
    )


class GasPriceFixedSerializer(serializers.Serializer):
    type = serializers.ReadOnlyField(default="fixed")
    value = serializers.CharField(source="gas_price_fixed")


class ThemeSerializer(serializers.Serializer):
    text_color = serializers.CharField(source="theme_text_color")
    background_color = serializers.CharField(source="theme_background_color")


class CurrencySerializer(serializers.Serializer):
    name = serializers.CharField(source="currency_name")
    symbol = serializers.CharField(source="currency_symbol")
    decimals = serializers.IntegerField(source="currency_decimals")
    logo_url = serializers.URLField(source="currency_logo_url")


class ChainSerializer(serializers.ModelSerializer):
    chain_id = serializers.CharField(source="id")
    chain_name = serializers.CharField(source="name")
    native_currency = serializers.SerializerMethodField()
    transaction_service = serializers.URLField(
        source="transaction_service_url", default=None
    )
    theme = serializers.SerializerMethodField()
    gas_price = serializers.SerializerMethodField()
    ens_registry_address = EthereumAddressField()

    class Meta:
        model = Chain
        fields = [
            "chain_id",
            "chain_name",
            "rpc_url",
            "block_explorer_url",
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
    def get_gas_price(obj):
        if obj.gas_price_oracle_url and obj.gas_price_fixed is None:
            return GasPriceOracleSerializer(obj).data
        elif obj.gas_price_fixed and obj.gas_price_oracle_url is None:
            return GasPriceFixedSerializer(obj).data
        else:
            raise APIException(
                f"Both or Neither the Price Oracle or Gas Price were provided for chain {obj.id}"
            )
