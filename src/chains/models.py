from django.db import models


class Chain(models.Model):
    id = models.PositiveBigIntegerField(verbose_name="Chain Id", primary_key=True)
    name = models.CharField(verbose_name="Chain name", max_length=255)
    rpc_url = models.URLField()
    block_explorer_url = models.URLField(null=True)
    currency_name = models.CharField(null=True, max_length=255)
    currency_symbol = models.CharField(max_length=255)
    currency_decimals = models.IntegerField(default=18)
    transaction_service_url = models.URLField(null=True)

    def __str__(self):
        return f"{self.name} | chain_id={self.id}"
