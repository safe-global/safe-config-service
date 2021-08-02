import logging
from functools import cache
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Chain

logger = logging.getLogger(__name__)


@cache
def setup_session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


@receiver(post_save, sender=Chain)
@receiver(post_delete, sender=Chain)
def on_chain_update(sender, **kwargs):
    logger.info("Chain update. Triggering CGW webhook")
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
