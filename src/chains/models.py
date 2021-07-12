import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from gnosis.eth.django.models import EthereumAddressField

HEX_ARGB_REGEX = re.compile("^#[0-9a-fA-F]{6}$")

color_validator = RegexValidator(HEX_ARGB_REGEX, "Invalid hex color", "invalid")

# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEM_VER_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"  # noqa E501
)

sem_ver_validator = RegexValidator(SEM_VER_REGEX, "Invalid version (semver)", "invalid")


class Chain(models.Model):
    id = models.PositiveBigIntegerField(verbose_name="Chain Id", primary_key=True)
    relevance = models.SmallIntegerField(
        default=100
    )  # A lower number will indicate more relevance
    name = models.CharField(verbose_name="Chain name", max_length=255)
    rpc_url = models.URLField()
    block_explorer_url = models.URLField(null=True)
    currency_name = models.CharField(null=True, max_length=255)
    currency_symbol = models.CharField(max_length=255)
    currency_decimals = models.IntegerField(default=18)
    currency_logo_url = models.URLField()
    transaction_service_url = models.URLField(null=True)
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
    gas_price_oracle_url = models.URLField(blank=True, null=True)
    gas_price_oracle_parameter = models.CharField(blank=True, null=True, max_length=255)
    ens_registry_address = EthereumAddressField(null=True, blank=True)
    gas_price_oracle_gwei_factor = models.DecimalField(
        default=1,
        max_digits=19,
        decimal_places=9,
        verbose_name="Gwei multiplier factor",
        help_text="Factor required to reach the Gwei unit",
    )
    min_master_copy_version = models.CharField(
        max_length=255, validators=[sem_ver_validator]
    )

    def clean(self):
        if self.gas_price_oracle_parameter and self.gas_price_oracle_url is None:
            raise ValidationError(
                {
                    "gas_price_oracle_parameter": "An oracle parameter was set with no Oracle url"
                }
            )

    def __str__(self):
        return f"{self.name} | chain_id={self.id}"
