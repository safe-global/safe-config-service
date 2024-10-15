import os
import re
from typing import IO, Union
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import QuerySet
from gnosis.eth.django.models import EthereumAddressField, Uint256Field

HEX_ARGB_REGEX = re.compile("^#[0-9a-fA-F]{6}$")

color_validator = RegexValidator(HEX_ARGB_REGEX, "Invalid hex color", "invalid")

# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEM_VER_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"  # noqa E501
)

sem_ver_validator = RegexValidator(SEM_VER_REGEX, "Invalid version (semver)", "invalid")


def logo_path(instance: "Chain", filename: str, pathname: str) -> str:
    _, file_extension = os.path.splitext(filename)  # file_extension includes the dot
    return f"chains/{instance.id}/{pathname}{file_extension}"


def chain_logo_path(instance: "Chain", filename: str) -> str:
    return logo_path(instance, filename, "chain_logo")


def native_currency_path(instance: "Chain", filename: str) -> str:
    return logo_path(instance, filename, "currency_logo")


def validate_native_currency_size(image: Union[str, IO[bytes]]) -> None:
    image_width, image_height = get_image_dimensions(
        image
    )  # (Optional[Int], Optional[Int])
    if not image_width or not image_height:
        raise ValidationError(
            f"Could not get image dimensions. Width={image_width}, Height={image_height}"
        )
    if image_width > 512 or image_height > 512:
        raise ValidationError("Image width and height need to be at most 512 pixels")


def validate_tx_service_url(url: str) -> None:
    result = urlparse(url)
    if not all(
        (
            result.scheme
            in (
                "http",
                "https",
            ),
            result.netloc,
        )
    ):
        raise ValidationError(f"{url} is not a valid url")


class Chain(models.Model):
    class RpcAuthentication(models.TextChoices):
        API_KEY_PATH = "API_KEY_PATH"
        NO_AUTHENTICATION = "NO_AUTHENTICATION"

    id = models.PositiveBigIntegerField(verbose_name="Chain Id", primary_key=True)
    relevance = models.SmallIntegerField(
        default=100
    )  # A lower number will indicate more relevance
    name = models.CharField(verbose_name="Chain name", max_length=255)
    short_name = models.CharField(
        verbose_name="EIP-3770 short name", max_length=255, unique=True
    )
    description = models.CharField(max_length=255, blank=True)
    chain_logo_uri = models.ImageField(
        validators=[
            validate_native_currency_size
        ],  # not renamed as used in older migration
        upload_to=chain_logo_path,
        max_length=255,
        null=True,
        blank=True,
    )
    l2 = models.BooleanField()
    is_testnet = models.BooleanField(default=False)
    rpc_authentication = models.CharField(
        max_length=255, choices=RpcAuthentication.choices
    )
    rpc_uri = models.URLField()
    safe_apps_rpc_authentication = models.CharField(
        max_length=255,
        choices=RpcAuthentication.choices,
        default=RpcAuthentication.NO_AUTHENTICATION,
    )
    safe_apps_rpc_uri = models.URLField(default="")
    public_rpc_authentication = models.CharField(
        max_length=255,
        choices=RpcAuthentication.choices,
        default=RpcAuthentication.NO_AUTHENTICATION,
    )
    public_rpc_uri = models.URLField()
    block_explorer_uri_address_template = models.URLField()
    block_explorer_uri_tx_hash_template = models.URLField()
    block_explorer_uri_api_template = models.URLField()
    beacon_chain_explorer_uri_public_key_template = models.URLField(
        blank=True, null=True
    )
    currency_name = models.CharField(max_length=255)
    currency_symbol = models.CharField(max_length=255)
    currency_decimals = models.IntegerField(default=18)
    currency_logo_uri = models.ImageField(
        validators=[validate_native_currency_size],
        upload_to=native_currency_path,
        max_length=255,
    )
    transaction_service_uri = models.CharField(
        max_length=255, validators=[validate_tx_service_url]
    )
    vpc_transaction_service_uri = models.CharField(
        max_length=255, validators=[validate_tx_service_url]
    )
    theme_text_color = models.CharField(
        validators=[color_validator],
        max_length=9,
        default="#ffffff",
        help_text="Please use the following format: <em>#RRGGBB</em>.",
    )
    theme_background_color = models.CharField(
        validators=[color_validator],
        max_length=9,
        default="#000000",
        help_text="Please use the following format: <em>#RRGGBB</em>.",
    )
    ens_registry_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    recommended_master_copy_version = models.CharField(
        max_length=255, validators=[sem_ver_validator]
    )
    prices_provider_native_coin = models.CharField(
        max_length=255, null=True, blank=True
    )
    prices_provider_chain_name = models.CharField(max_length=255, null=True, blank=True)
    balances_provider_chain_name = models.CharField(
        max_length=255, null=True, blank=True
    )
    balances_provider_enabled = models.BooleanField(
        default=False,
        help_text="This flag informs API clients whether the balances provider is enabled for the chain",
    )
    hidden = models.BooleanField(default=False)
    safe_singleton_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    safe_proxy_factory_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    multi_send_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    multi_send_call_only_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    fallback_handler_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    sign_message_lib_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    create_call_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    simulate_tx_accessor_address = EthereumAddressField(null=True, blank=True)  # type: ignore[no-untyped-call]
    safe_web_authn_signer_factory_address = EthereumAddressField(
        null=True, blank=True
    )  # type: ignore[no-untyped-call]

    def get_disabled_wallets(self) -> QuerySet["Wallet"]:
        all_wallets = Wallet.objects.all()
        enabled_wallets = self.wallet_set.all()

        return all_wallets.difference(enabled_wallets)

    def __str__(self) -> str:
        return f"{self.name} | chain_id={self.id}"


class GasPrice(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE)
    oracle_uri = models.URLField(blank=True, null=True)
    oracle_parameter = models.CharField(blank=True, null=True, max_length=255)
    gwei_factor = models.DecimalField(
        default=1,
        max_digits=19,
        decimal_places=9,
        verbose_name="Gwei multiplier factor",
        help_text="Factor required to reach the Gwei unit",
    )
    fixed_wei_value = Uint256Field(
        verbose_name="Fixed gas price (wei)", blank=True, null=True
    )  # type: ignore[no-untyped-call]
    rank = models.SmallIntegerField(
        default=100
    )  # A lower number will indicate higher ranking
    max_fee_per_gas = Uint256Field(
        verbose_name="Max fee per gas (wei)", blank=True, null=True
    )  # type: ignore[no-untyped-call]
    max_priority_fee_per_gas = Uint256Field(
        verbose_name="Max priority fee per gas (wei)", blank=True, null=True
    )  # type: ignore[no-untyped-call]

    def __str__(self) -> str:
        return f"Chain = {self.chain.id} | uri={self.oracle_uri} | fixed_wei_value={self.fixed_wei_value} | max_fee_per_gas={self.max_fee_per_gas} | max_priority_fee_per-gas={self.max_priority_fee_per_gas}"  # noqa E501

    def clean(self) -> None:
        fixed_wei_defined = self.fixed_wei_value is not None
        fixed1559_defined = (
            self.max_fee_per_gas is not None
            and self.max_priority_fee_per_gas is not None
        )
        oracle_defined = self.oracle_uri is not None
        exactly_one_variant = [
            fixed_wei_defined,
            fixed1559_defined,
            oracle_defined,
        ].count(True) == 1
        multiple_variants_error = "An oracle uri, fixed gas price or maxFeePerGas and maxPriorityFeePerGas \
            should be provided (but not multiple)"
        if not exactly_one_variant:
            raise ValidationError(
                {
                    "oracle_uri": multiple_variants_error,
                    "fixed_wei_value": multiple_variants_error,
                    "max_fee_per_gas": multiple_variants_error,
                    "max_priority_fee_per_gas": multiple_variants_error,
                }
            )
        if self.oracle_uri is not None and self.oracle_parameter is None:
            raise ValidationError(
                {"oracle_parameter": "The oracle parameter should be set"}
            )


class Wallet(models.Model):
    # A wallet can be part of multiple Chains and a Chain can have multiple Wallets
    chains = models.ManyToManyField(
        Chain, blank=True, help_text="Chains where this wallet is enabled."
    )
    key = models.CharField(
        unique=True,
        max_length=255,
        help_text="The unique name/key that identifies this wallet",
    )

    def __str__(self) -> str:
        return f"Wallet: {self.key}"


class Feature(models.Model):
    # A feature can be enabled for multiple Chains and a Chain can have multiple features enabled
    chains = models.ManyToManyField(
        Chain, blank=True, help_text="Chains where this feature is enabled."
    )
    key = models.CharField(
        unique=True,
        max_length=255,
        help_text="The unique name/key that identifies this feature",
    )

    def __str__(self) -> str:
        return f"Chain Feature: {self.key}"
