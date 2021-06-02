from django.db import models


class Chain(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    rpc_url = models.URLField()
    block_explorer_url = models.URLField(null=True)
    currency_name = models.CharField(null=True, max_length=255)
    currency_symbol = models.CharField(max_length=255)
    currency_decimals = models.IntegerField(default=18)

    def __str__(self):
        return f"{self.name} | chain_id={self.id}"
