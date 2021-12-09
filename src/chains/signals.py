import logging
from functools import cache
from typing import Any
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Chain, Feature, GasPrice, Wallet

logger = logging.getLogger(__name__)


@cache
def setup_session() -> requests.Session:
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _trigger_client_gateway_flush() -> None:
    cgw_url = settings.CGW_URL
    if cgw_url is None:
        logger.error("CGW_URL is not set. Skipping hook call")
        return
    cgw_flush_token = settings.CGW_FLUSH_TOKEN
    if cgw_flush_token is None:
        logger.error("CGW_FLUSH_TOKEN is not set. Skipping hook call")
        return

    url = urljoin(cgw_url, f"/v1/flush/{cgw_flush_token}")
    try:
        post = setup_session().post(url, json={"invalidate": "Chains"})
        post.raise_for_status()
    except Exception as error:
        logger.error(error)


@receiver(post_save, sender=Chain)
@receiver(post_delete, sender=Chain)
def on_chain_update(sender: Chain, **kwargs: Any) -> None:
    logger.info("Chain update. Triggering CGW webhook")
    _trigger_client_gateway_flush()


@receiver(post_save, sender=GasPrice)
@receiver(post_delete, sender=GasPrice)
def on_gas_price_update(sender: GasPrice, **kwargs: Any) -> None:
    logger.info("GasPrice update. Triggering CGW webhook")
    _trigger_client_gateway_flush()


@receiver(post_save, sender=Feature)
@receiver(post_delete, sender=Feature)
def on_feature_update(sender: Feature, **kwargs: Any) -> None:
    logger.info("Feature update. Triggering CGW webhook")
    _trigger_client_gateway_flush()


@receiver(post_save, sender=Wallet)
@receiver(post_delete, sender=Wallet)
def on_wallet_update(sender: Wallet, **kwargs: Any) -> None:
    logger.info("Wallet update. Triggering CGW webhook")
    _trigger_client_gateway_flush()
