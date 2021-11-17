import logging
from typing import Any

from django.core.cache import caches
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Provider, SafeApp

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SafeApp)
@receiver(post_delete, sender=SafeApp)
@receiver(post_save, sender=Provider)
@receiver(post_delete, sender=Provider)
def on_safe_app_update(sender: SafeApp, **kwargs: Any) -> None:
    logger.info("Clearing safe-apps cache")
    caches["safe-apps"].clear()
