import os
import uuid
from enum import Enum
from typing import IO, Union

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.validators import RegexValidator
from django.db import models

_HOSTNAME_VALIDATOR = RegexValidator(
    r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\/?$",
    message="Enter a valid hostname (Without a resource path)",
    code="invalid_hostname",
)


def safe_app_icon_path(instance: "SafeApp", filename: str) -> str:
    _, file_extension = os.path.splitext(filename)
    return f"safe_apps/{uuid.uuid4()}/icon{file_extension}"


def validate_safe_app_icon_size(image: Union[str, IO[bytes]]) -> None:
    width, height = get_image_dimensions(image)
    if not width or not height:
        raise ValidationError(
            f"Could not get image dimensions. Width={width}, Height={height}"
        )
    if width > 512 or height > 512:
        raise ValidationError("Image width and height need to be at most 512 pixels")


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
    listed = models.BooleanField(
        default=True
    )  # True if this safe-app should be listed in the view. False otherwise
    url = models.URLField()
    name = models.CharField(max_length=200)
    icon_url = models.ImageField(
        validators=[validate_safe_app_icon_size],
        upload_to=safe_app_icon_path,
        max_length=255,
        default="safe_apps/icon_url.jpg",
    )
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
    developer_website = models.URLField(null=True, blank=True)

    def get_access_control_type(self) -> AccessControlPolicy:
        if self.exclusive_clients.exists():
            return SafeApp.AccessControlPolicy.DOMAIN_ALLOWLIST
        return SafeApp.AccessControlPolicy.NO_RESTRICTIONS

    def __str__(self) -> str:
        return f"{self.name} | {self.url} | chain_ids={self.chain_ids}"


class Tag(models.Model):
    name = models.CharField(max_length=255)
    safe_apps = models.ManyToManyField(SafeApp, blank=True)

    def __str__(self) -> str:
        return f"Tag: {self.name}"


class Feature(models.Model):
    # A feature can be enabled for multiple Safe Apps and a Safe App can have multiple features enabled
    safe_apps = models.ManyToManyField(
        SafeApp, blank=True, help_text="Safe Apps where this feature is enabled."
    )
    key = models.CharField(
        unique=True,
        max_length=255,
        help_text="The unique name/key that identifies this feature",
    )

    def __str__(self) -> str:
        return f"Safe App Feature: {self.key}"


class SocialProfile(models.Model):
    class Platform(models.TextChoices):
        DISCORD = "DISCORD"
        GITHUB = "GITHUB"
        TWITTER = "TWITTER"

    safe_app = models.ForeignKey(SafeApp, on_delete=models.CASCADE)
    platform = models.CharField(choices=Platform.choices, max_length=255)
    url = models.URLField()

    def __str__(self) -> str:
        return f"Social Profile: {self.platform} | {self.url}"
