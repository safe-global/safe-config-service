from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import QuerySet


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

    def get_access_control_sources(self) -> QuerySet["Client"]:
        return Client.objects.filter(apps=self)

    def get_access_control_type(self) -> str:
        if len(self.get_access_control_sources()) > 0:
            return self.AccessControlPolicy.DOMAIN_ALLOWLIST
        return self.AccessControlPolicy.NO_RESTRICTIONS

    def __str__(self) -> str:
        return f"{self.name} | {self.url} | chain_ids={self.chain_ids}"


class Client(models.Model):
    # A client can have multiple Safe Apps and a Safe App can work on multiple clients
    apps = models.ManyToManyField(
        SafeApp, blank=True, help_text="Apps that are enabled exclusively for this client"
    )
    url = models.URLField(
        unique=True,
        help_text="The domain URL client is hosted at",
    )

    def __str__(self) -> str:
        return f"Client: {self.url}"
