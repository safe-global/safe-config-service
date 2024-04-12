import logging
from typing import Any

from django.core.cache import caches
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)
from django.dispatch import receiver

from clients.safe_client_gateway import HookEvent, hook_event

from .models import Feature, Provider, SafeApp, Tag

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=SafeApp)
def on_safe_app_update(sender: SafeApp, instance: SafeApp, **kwargs: Any) -> None:
    logger.info("Clearing safe-apps cache")
    caches["safe-apps"].clear()
    chain_ids = set(instance.chain_ids)
    if instance.app_id is not None:  # existing SafeApp being updated
        previous = SafeApp.objects.filter(app_id=instance.app_id).first()
        if previous is not None:
            chain_ids.update(previous.chain_ids)
    for chain_id in chain_ids:
        hook_event(HookEvent(type=HookEvent.Type.SAFE_APPS_UPDATE, chain_id=chain_id))


@receiver(post_delete, sender=SafeApp)
def on_safe_app_delete(sender: SafeApp, instance: SafeApp, **kwargs: Any) -> None:
    logger.info("Clearing safe-apps cache")
    caches["safe-apps"].clear()
    for chain_id in instance.chain_ids:
        hook_event(HookEvent(type=HookEvent.Type.SAFE_APPS_UPDATE, chain_id=chain_id))


@receiver(post_save, sender=Provider)
@receiver(post_delete, sender=Provider)
def on_provider_update(sender: Provider, instance: Provider, **kwargs: Any) -> None:
    logger.info("Clearing safe-apps cache")
    caches["safe-apps"].clear()
    for safe_app in instance.safeapp_set.all():
        for chain_id in safe_app.chain_ids:
            hook_event(
                HookEvent(type=HookEvent.Type.SAFE_APPS_UPDATE, chain_id=chain_id)
            )


# pre_delete is used because on pre_delete the model still has safe_apps
# which is not the case on post_delete
@receiver(post_save, sender=Tag)
@receiver(pre_delete, sender=Tag)
def on_tag_update(sender: Tag, instance: Tag, **kwargs: Any) -> None:
    logger.info("Clearing safe-apps cache")
    caches["safe-apps"].clear()
    for safe_app in instance.safe_apps.all():
        for chain_id in safe_app.chain_ids:
            hook_event(
                HookEvent(type=HookEvent.Type.SAFE_APPS_UPDATE, chain_id=chain_id)
            )


@receiver(m2m_changed, sender=Tag.safe_apps.through)
def on_tag_chains_update(
    sender: Tag, instance: Tag, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("TagChains update. Triggering CGW webhook")
    caches["safe-apps"].clear()
    if action == "post_add" or action == "post_remove":
        chain_ids = set()
        for safe_app in SafeApp.objects.filter(app_id__in=pk_set):
            for chain_id in safe_app.chain_ids:
                chain_ids.add(chain_id)
        for chain_id in chain_ids:
            hook_event(
                HookEvent(type=HookEvent.Type.SAFE_APPS_UPDATE, chain_id=chain_id)
            )


# pre_delete is used because on pre_delete the model still has safe_apps
# which is not the case on post_delete
@receiver(post_save, sender=Feature)
@receiver(pre_delete, sender=Feature)
def on_feature_update(sender: Feature, instance: Feature, **kwargs: Any) -> None:
    logger.info("Feature update. Triggering CGW webhook")
    caches["safe-apps"].clear()
    for safe_app in instance.safe_apps.all():
        for chain_id in safe_app.chain_ids:
            hook_event(
                HookEvent(type=HookEvent.Type.SAFE_APPS_UPDATE, chain_id=chain_id)
            )


@receiver(m2m_changed, sender=Feature.safe_apps.through)
def on_feature_safe_apps_update(
    sender: Feature, instance: Feature, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("FeatureSafeApps update. Triggering CGW webhook")
    caches["safe-apps"].clear()
    if action == "post_add" or action == "post_remove":
        chain_ids = set()
        for safe_app in SafeApp.objects.filter(app_id__in=pk_set):
            for chain_id in safe_app.chain_ids:
                chain_ids.add(chain_id)
        for chain_id in chain_ids:
            hook_event(
                HookEvent(type=HookEvent.Type.SAFE_APPS_UPDATE, chain_id=chain_id)
            )
