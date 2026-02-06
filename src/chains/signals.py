import logging
from typing import Any

from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver

from clients.safe_client_gateway import HookEvent, hook_event

from .models import Chain, Feature, GasPrice, Service, Wallet

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Chain)
@receiver(post_delete, sender=Chain)
def on_chain_update(sender: Chain, instance: Chain, **kwargs: Any) -> None:
    logger.info("Chain update. Triggering CGW webhook")
    hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=instance.id))


@receiver(post_save, sender=GasPrice)
@receiver(post_delete, sender=GasPrice)
def on_gas_price_update(sender: GasPrice, instance: GasPrice, **kwargs: Any) -> None:
    logger.info("GasPrice update. Triggering CGW webhook")
    hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=instance.chain.id))


# We need to store the old scope in the instance to handle scope changes
# Feature scope changes are handled by the on_feature_scope_change_post_save signal
@receiver(pre_save, sender=Feature)
def on_feature_scope_change_pre_save(sender: Feature, instance: Feature, **kwargs: Any) -> None:
    if instance.pk:
        try:
            old_instance = Feature.objects.get(pk=instance.pk)
            instance._old_scope = old_instance.scope
        except Feature.DoesNotExist:
            instance._old_scope = None
    else:
        instance._old_scope = None


# pre_delete is used because on pre_delete the model still has chains
# which is not the case on post_delete
@receiver(post_save, sender=Feature)
@receiver(pre_delete, sender=Feature)
def on_feature_changed(sender: Feature, instance: Feature, **kwargs: Any) -> None:
    logger.info("Feature update. Triggering CGW webhook")
    service_keys = list(instance.services.values_list("key", flat=True))
    old_scope = getattr(instance, '_old_scope', None)

    if old_scope and old_scope != instance.scope:
        # Scope changes are handled by the on_feature_scope_change_post_save signal
        return

    if instance.scope == Feature.Scope.GLOBAL:
        # GLOBAL features affect all chains
        chains = Chain.objects.all()
    else:
        # PER_CHAIN features only affect their assigned chains
        chains = instance.chains.all()

    for chain in chains:
        if service_keys:
            for service_key in service_keys:
                hook_event(
                    HookEvent(
                        type=HookEvent.Type.CHAIN_UPDATE,
                        chain_id=chain.id,
                        service=service_key,
                    )
                )
        else:
            hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=chain.id))


# Feature scope changes from GLOBAL to PER_CHAIN or vice versa are handled by this signal
# This is because the scope change affects all the chains
@receiver(post_save, sender=Feature)
def on_feature_scope_change_post_save(sender: Feature, instance: Feature, **kwargs: Any) -> None:
    old_scope = getattr(instance, '_old_scope', None)
    current_scope = instance.scope

    if old_scope and old_scope != current_scope:
        logger.info("Feature scope changed from %s to %s. Triggering CGW webhook", old_scope, current_scope)
        service_keys = list(instance.services.values_list("key", flat=True))
        chains = Chain.objects.all()

        for chain in chains:
            if service_keys:
                for service_key in service_keys:
                    hook_event(
                        HookEvent(
                            type=HookEvent.Type.CHAIN_UPDATE,
                            chain_id=chain.id,
                            service=service_key,
                        )
                    )
            else:
                hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=chain.id))

        # Clear the old scope to avoid interfering with subsequent operations
        instance._old_scope = None


@receiver(m2m_changed, sender=Feature.chains.through)
def on_feature_chains_changed(
    sender: Feature, instance: Feature, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("FeatureChains update. Triggering CGW webhook")
    old_scope = getattr(instance, '_old_scope', None)

    if old_scope and old_scope != instance.scope:
        # Scope changes are handled by the on_feature_scope_change_post_save signal
        return

    if action == "post_add" or action == "post_remove":
        service_keys = list(instance.services.values_list("key", flat=True))
        for chain_id in pk_set:
            if service_keys:
                for service_key in service_keys:
                    hook_event(
                        HookEvent(
                            type=HookEvent.Type.CHAIN_UPDATE,
                            chain_id=chain_id,
                            service=service_key,
                        )
                    )
            else:
                hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=chain_id))


@receiver(m2m_changed, sender=Feature.services.through)
def on_feature_services_changed(
    sender: Feature, instance: Feature, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("FeatureServices update. Triggering CGW webhook")
    if action == "post_add" or action == "post_remove":
        affected_service_keys = list(
            Service.objects.filter(pk__in=pk_set).values_list("key", flat=True)
        )
        if instance.scope == Feature.Scope.GLOBAL:
            chains = Chain.objects.all()
        else:
            chains = instance.chains.all()

        for chain in chains:
            for service_key in affected_service_keys:
                logger.info(
                    "======================= FeatureServices update. Triggering CGW webhook for chain: %s, service: %s",
                    chain.id,
                    service_key,
                )
                hook_event(
                    HookEvent(
                        type=HookEvent.Type.CHAIN_UPDATE,
                        chain_id=chain.id,
                        service=service_key,
                    )
                )


# pre_delete is used because on pre_delete the model still has chains
# which is not the case on post_delete
@receiver(post_save, sender=Wallet)
@receiver(pre_delete, sender=Wallet)
def on_wallet_changed(sender: Wallet, instance: Wallet, **kwargs: Any) -> None:
    logger.info("Wallet update. Triggering CGW webhook")
    # A Wallet change affects all the chains that have this wallet
    for chain in instance.chains.all():
        hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=chain.id))


@receiver(m2m_changed, sender=Wallet.chains.through)
def on_wallet_chains_changed(
    sender: Wallet, instance: Wallet, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("WalletChains update. Triggering CGW webhook")
    if action == "post_add" or action == "post_remove":
        for chain_id in pk_set:
            hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=chain_id))
