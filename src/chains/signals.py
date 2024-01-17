import logging
from typing import Any

from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete
from django.dispatch import receiver

from clients.safe_client_gateway import HookEvent, hook_event

from .models import Chain, Feature, GasPrice, Wallet

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


# pre_delete is used because on pre_delete the model still has chains
# which is not the case on post_delete
@receiver(post_save, sender=Feature)
@receiver(pre_delete, sender=Feature)
def on_feature_changed(sender: Feature, instance: Feature, **kwargs: Any) -> None:
    logger.info("Feature update. Triggering CGW webhook")
    # A Feature change affects all the chains that have this feature
    for chain in instance.chains.all():
        hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=chain.id))


@receiver(m2m_changed, sender=Feature.chains.through)
def on_feature_chains_changed(
    sender: Feature, instance: Feature, action: str, pk_set: set[int], **kwargs: Any
) -> None:
    logger.info("FeatureChains update. Triggering CGW webhook")
    if action == "post_add" or action == "post_remove":
        for chain_id in pk_set:
            hook_event(HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=chain_id))


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
