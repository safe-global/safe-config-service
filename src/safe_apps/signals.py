import logging
from typing import Any

from django.conf import settings
from django.core.cache import caches
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

import clients.safe_client_gateway

from .models import Provider, SafeApp, Tag

logger = logging.getLogger(__name__)


def _flush_cgw_safe_apps() -> None:
    clients.safe_client_gateway.flush(
        cgw_url=settings.CGW_URL,
        cgw_flush_token=settings.CGW_FLUSH_TOKEN,
        # Even though the payload is Chains, it actually invalidates all the safe-config related cache
        json={"invalidate": "Chains"},
    )


@receiver(post_save, sender=SafeApp)
@receiver(post_delete, sender=SafeApp)
@receiver(post_save, sender=Provider)
@receiver(post_delete, sender=Provider)
@receiver(post_save, sender=Tag)
@receiver(post_delete, sender=Tag)
def on_safe_app_update(sender: SafeApp, **kwargs: Any) -> None:
    logger.info("Clearing safe-apps cache")
    caches["safe-apps"].clear()
    _flush_cgw_safe_apps()
