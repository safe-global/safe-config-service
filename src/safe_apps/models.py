from django.contrib.postgres.fields import ArrayField
from django.db import models


class Provider(models.Model):
    url = models.URLField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.name} | {self.url}"


class SafeApp(models.Model):
    class AccessControlPolicy(models.TextChoices):
        NO_RESTRICTIONS = "NO_RESTRICTIONS"
        DOMAIN_ALLOWLIST = "DOMAIN_ALLOWLIST"

    app_id = models.BigAutoField(primary_key=True)
    visible = models.BooleanField(
        default=True
    )  # True if this safe-app should be visible from the view. False otherwise
    url = models.URLField()
    name = models.CharField(max_length=200)
    icon_url = models.URLField()
    description = models.CharField(max_length=200)
    chain_ids = ArrayField(models.PositiveBigIntegerField())
    provider = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.SET_NULL
    )
    access_control_type=models.CharField(
        max_length=255,
        choices=AccessControlPolicy.choices,
        default=AccessControlPolicy.NO_RESTRICTIONS,
    )
    access_control_sources=ArrayField(models.URLField(), null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name} | {self.url} | chain_ids={self.chain_ids}"
