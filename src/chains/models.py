import re

from django.core.validators import RegexValidator
from django.db import models

HEX_ARGB_REGEX = re.compile("^#(?:[0-9a-fA-F]{3,4}){1,2}$")

color_validator = RegexValidator(HEX_ARGB_REGEX, "Invalid hex color", "invalid")


class Chain(models.Model):
    id = models.PositiveBigIntegerField(verbose_name="Chain Id", primary_key=True)
    name = models.CharField(verbose_name="Chain name", max_length=255)
    rpc_url = models.URLField()
    block_explorer_url = models.URLField(null=True)
    currency_name = models.CharField(null=True, max_length=255)
    currency_symbol = models.CharField(max_length=255)
    currency_decimals = models.IntegerField(default=18)
    transaction_service_url = models.URLField(null=True)
    theme_text_color = models.CharField(
        validators=[color_validator], max_length=9, default="#fff"
    )
    theme_background_color = models.CharField(
        validators=[color_validator], max_length=9, default="#000"
    )

    def __str__(self):
        return f"{self.name} | chain_id={self.id}"
