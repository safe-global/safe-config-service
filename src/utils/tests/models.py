from django.db import models

from ..validators.hostname import HostnameValidator


class HostnameExample(models.Model):
    """
    A model for testing HostnameValidator
    """

    hostname = models.CharField(
        blank=True, max_length=255, validators=[HostnameValidator]
    )

    def __str__(self):
        return f"Hostname: {self.domain}"
