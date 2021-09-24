import os
import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from gnosis.eth.django.models import EthereumAddressField, Uint256Field

HEX_ARGB_REGEX = re.compile("^#[0-9a-fA-F]{6}$")

color_validator = RegexValidator(HEX_ARGB_REGEX, "Invalid hex color", "invalid")

# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEM_VER_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"  # noqa E501
)

sem_ver_validator = RegexValidator(SEM_VER_REGEX, "Invalid version (semver)", "invalid")


def native_currency_path(instance: "Chain", filename):
    _, file_extension = os.path.splitext(filename)  # file_extension includes the dot
    return f"chains/{instance.id}/currency_logo{file_extension}"


class Chain(models.Model):
    class RpcAuthentication(models.TextChoices):
        API_KEY_PATH = "API_KEY_PATH"
        NO_AUTHENTICATION = "NO_AUTHENTICATION"

    id = models.PositiveBigIntegerField(verbose_name="Chain Id", primary_key=True)
    relevance = models.SmallIntegerField(
        default=100
    )  # A lower number will indicate more relevance
    name = models.CharField(verbose_name="Chain name", max_length=255)
    description = models.CharField(max_length=255, blank=True)
    l2 = models.BooleanField()
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
    block_explorer_uri_address_template = models.URLField()
    block_explorer_uri_tx_hash_template = models.URLField()
    currency_name = models.CharField(max_length=255)
    currency_symbol = models.CharField(max_length=255)
    currency_decimals = models.IntegerField(default=18)
    currency_logo_uri = models.URLField(default="")
    transaction_service_uri = models.URLField()
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
    ens_registry_address = EthereumAddressField(null=True, blank=True)

    recommended_master_copy_version = models.CharField(
        max_length=255, validators=[sem_ver_validator]
    )

    def __str__(self):
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
    )
    rank = models.SmallIntegerField(
        default=100
    )  # A lower number will indicate higher ranking

    def __str__(self):
        return f"Chain = {self.chain.id} | uri={self.oracle_uri} | fixed_wei_value={self.fixed_wei_value}"

    def clean(self):
        if (self.fixed_wei_value is not None) == (self.oracle_uri is not None):
            raise ValidationError(
                {
                    "oracle_uri": "An oracle uri or fixed gas price should be provided (but not both)",
                    "fixed_wei_value": "An oracle uri or fixed gas price should be provided (but not both)",
                }
            )
        if self.oracle_uri is not None and self.oracle_parameter is None:
            raise ValidationError(
                {"oracle_parameter": "The oracle parameter should be set"}
            )
