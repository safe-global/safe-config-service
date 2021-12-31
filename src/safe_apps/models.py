from enum import Enum

from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models

_HOSTNAME_VALIDATOR = RegexValidator(
    r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\/?$",
    message="Enter a valid hostname (Without a resource path)",
    code="invalid_hostname",
)


class Provider(models.Model):
    url = models.URLField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.name} | {self.url}"


class Client(models.Model):
    url = models.CharField(
        unique=True,
        help_text="The domain URL client is hosted at",
        # The maximum length of a full host name is 253 characters per RFC 1034
        max_length=255,
        validators=[_HOSTNAME_VALIDATOR],
    )

    def __str__(self) -> str:
        return f"Client: {self.url}"


class SafeApp(models.Model):
    class AccessControlPolicy(str, Enum):
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
    exclusive_clients = models.ManyToManyField(
        Client,
        blank=True,
        help_text="Clients that are only allowed to use this SafeApp",
    )

    def get_access_control_type(self) -> AccessControlPolicy:
        if self.exclusive_clients.exists():
            return SafeApp.AccessControlPolicy.DOMAIN_ALLOWLIST
        return SafeApp.AccessControlPolicy.NO_RESTRICTIONS

    def __str__(self) -> str:
        return f"{self.name} | {self.url} | chain_ids={self.chain_ids}"
