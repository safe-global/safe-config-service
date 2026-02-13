import logging
import threading
from typing import Any

from django.core.signals import request_finished
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver

from .models import Chain, Feature, GasPrice, Service, Wallet
from .services import ChainUpdateWebhookService

logger = logging.getLogger(__name__)
webhook_service = ChainUpdateWebhookService()

_feature_scope_storage = threading.local()


def _get_feature_old_scope(instance: Feature) -> str | None:
    cache = getattr(_feature_scope_storage, "cache", None)
    return cache.get(id(instance)) if cache else None


def _set_feature_old_scope(instance: Feature, scope: str | None) -> None:
    if not hasattr(_feature_scope_storage, "cache"):
        _feature_scope_storage.cache = {}
    _feature_scope_storage.cache[id(instance)] = scope


def _clear_feature_old_scope(instance: Feature) -> None:
    cache = getattr(_feature_scope_storage, "cache", None)
    if cache is not None and id(instance) in cache:
        del cache[id(instance)]


@receiver(request_finished)
def _clear_feature_scope_cache(**kwargs: Any) -> None:
    if hasattr(_feature_scope_storage, "cache"):
        _feature_scope_storage.cache.clear()


@receiver(post_save, sender=Chain)
@receiver(post_delete, sender=Chain)
def on_chain_update(sender: Chain, instance: Chain, **kwargs: Any) -> None:
    logger.info("Chain update. Triggering CGW webhook")
    webhook_service.notify([instance.id])


@receiver(post_save, sender=GasPrice)
@receiver(post_delete, sender=GasPrice)
def on_gas_price_update(sender: GasPrice, instance: GasPrice, **kwargs: Any) -> None:
    logger.info("GasPrice update. Triggering CGW webhook")
    webhook_service.notify([instance.chain.id])


# We need to store the old scope in the instance to handle scope changes
# Feature scope changes are handled by the on_feature_scope_change_post_save signal
@receiver(pre_save, sender=Feature)
def on_feature_scope_change_pre_save(sender: Feature, instance: Feature, **kwargs: Any) -> None:
    if instance.pk:
        try:
            old_instance = Feature.objects.get(pk=instance.pk)
            _set_feature_old_scope(instance, old_instance.scope)
        except Feature.DoesNotExist:
            _set_feature_old_scope(instance, None)
    else:
        _set_feature_old_scope(instance, None)


# pre_delete is used because on pre_delete the model still has chains
# which is not the case on post_delete
@receiver(post_save, sender=Feature)
@receiver(pre_delete, sender=Feature)
def on_feature_changed(sender: Feature, instance: Feature, **kwargs: Any) -> None:
    logger.info("Feature update. Triggering CGW webhook")
    old_scope = _get_feature_old_scope(instance)
    if old_scope and old_scope != instance.scope:
        return

    service_keys = list(instance.services.values_list("key", flat=True)) or None
    chain_ids = (
        Chain.objects.values_list("id", flat=True)
        if instance.scope == Feature.Scope.GLOBAL
        else instance.chains.values_list("id", flat=True)
    )
    webhook_service.notify(chain_ids, service_keys)


@receiver(post_save, sender=Feature)
def on_feature_scope_change_post_save(sender: Feature, instance: Feature, **kwargs: Any) -> None:
    old_scope = _get_feature_old_scope(instance)
    if not old_scope or old_scope == instance.scope:
        return

    logger.info(
        "Feature scope changed from %s to %s. Triggering CGW webhook",
        old_scope,
        instance.scope,
    )
    service_keys = list(instance.services.values_list("key", flat=True)) or None
    chain_ids = Chain.objects.values_list("id", flat=True)
    webhook_service.notify(chain_ids, service_keys)
    _clear_feature_old_scope(instance)


@receiver(m2m_changed, sender=Feature.chains.through)
def on_feature_chains_changed(
    sender: Feature, instance: Feature, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("FeatureChains update. Triggering CGW webhook")
    old_scope = _get_feature_old_scope(instance)
    if old_scope and old_scope != instance.scope:
        return

    if action in ("post_add", "post_remove"):
        service_keys = list(instance.services.values_list("key", flat=True)) or None
        webhook_service.notify(pk_set, service_keys)


@receiver(m2m_changed, sender=Feature.services.through)
def on_feature_services_changed(
    sender: Feature, instance: Feature, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("FeatureServices update. Triggering CGW webhook")
    if action in ("post_add", "post_remove"):
        affected_service_keys = list(
            Service.objects.filter(pk__in=pk_set).values_list("key", flat=True)
        )
        chain_ids = (
            Chain.objects.values_list("id", flat=True)
            if instance.scope == Feature.Scope.GLOBAL
            else instance.chains.values_list("id", flat=True)
        )
        webhook_service.notify(chain_ids, affected_service_keys)


@receiver(post_save, sender=Wallet)
@receiver(pre_delete, sender=Wallet)
def on_wallet_changed(sender: Wallet, instance: Wallet, **kwargs: Any) -> None:
    logger.info("Wallet update. Triggering CGW webhook")
    chain_ids = instance.chains.values_list("id", flat=True)
    webhook_service.notify(chain_ids)


@receiver(m2m_changed, sender=Wallet.chains.through)
def on_wallet_chains_changed(
    sender: Wallet, instance: Wallet, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("WalletChains update. Triggering CGW webhook")
    if action in ("post_add", "post_remove"):
        webhook_service.notify(pk_set)
