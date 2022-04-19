import logging
from typing import Any

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

import clients.safe_client_gateway

from .models import Chain, Feature, GasPrice, Wallet

logger = logging.getLogger(__name__)


def _flush_cgw_chains() -> None:
    clients.safe_client_gateway.flush(
        cgw_url=settings.CGW_URL,
        cgw_flush_token=settings.CGW_FLUSH_TOKEN,
        json={"invalidate": "Chains"},
    )


@receiver(post_save, sender=Chain)
@receiver(post_delete, sender=Chain)
def on_chain_update(sender: Chain, **kwargs: Any) -> None:
    logger.info("Chain update. Triggering CGW webhook")
    _flush_cgw_chains()


@receiver(post_save, sender=GasPrice)
@receiver(post_delete, sender=GasPrice)
def on_gas_price_update(sender: GasPrice, **kwargs: Any) -> None:
    logger.info("GasPrice update. Triggering CGW webhook")
    _flush_cgw_chains()


@receiver(post_save, sender=Feature)
@receiver(post_delete, sender=Feature)
def on_feature_update(sender: Feature, **kwargs: Any) -> None:
    logger.info("Feature update. Triggering CGW webhook")
    _flush_cgw_chains()


@receiver(post_save, sender=Wallet)
@receiver(post_delete, sender=Wallet)
def on_wallet_update(sender: Wallet, **kwargs: Any) -> None:
    logger.info("Wallet update. Triggering CGW webhook")
    _flush_cgw_chains()
