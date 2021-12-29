from enum import Enum

from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models


def _hostname_validator() -> RegexValidator:
    """
    This is a modified Django URLValidator with dropped additional checks.
    https://github.com/django/django/blob/e8b4feddc34ffe5759ec21da8fa027e86e653f1c/django/core/validators.py#L63
    """

    ul = "\u00a1-\uffff"  # unicode letters range (must not be a raw string)

    # IP patterns
    ipv4_re = (
        r"(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}"
    )
    ipv6_re = r"\[[0-9a-f:\.]+\]"  # (simple regex, validated later)

    # Host patterns
    hostname_re = (
        r"[a-z" + ul + r"0-9](?:[a-z" + ul + r"0-9-]{0,61}[a-z" + ul + r"0-9])?"
    )
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = r"(?:\.(?!-)[a-z" + ul + r"0-9-]{1,63}(?<!-))*"
    tld_re = (
        r"\."  # dot
        r"(?!-)"  # can't start with a dash
        r"(?:[a-z" + ul + "-]{2,63}"  # domain label
        r"|xn--[a-z0-9]{1,59})"  # or punycode label
        r"(?<!-)"  # can't end with a dash
        r"\.?"  # may have a trailing dot
        r"/?"
    )
    host_re = "(" + hostname_re + domain_re + tld_re + ")"
    regex = (
        r"(?:" + ipv4_re + "|" + ipv6_re + "|" + host_re + ")"
        r"(?::\d{2,5})?"  # port
        r"\Z"
    )
    return RegexValidator(
        regex,
        message="Enter a valid hostname (Without a resource path)",
        code="invalid_hostname",
    )


HostnameValidator = _hostname_validator()


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
        validators=[HostnameValidator],
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
