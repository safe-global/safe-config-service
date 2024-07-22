import logging
from dataclasses import dataclass
from enum import Enum
from functools import cache
from typing import Any, Dict
from urllib.parse import urljoin

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class HookEvent:
    class Type(str, Enum):
        CHAIN_UPDATE = "CHAIN_UPDATE"
        SAFE_APPS_UPDATE = "SAFE_APPS_UPDATE"

    type: Type
    chain_id: int


@cache
def setup_session() -> requests.Session:
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        max_retries=settings.CGW_SESSION_MAX_RETRIES
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def cgw_setup() -> tuple[str, str]:
    if settings.CGW_URL is None:
        raise ValueError("CGW_URL is not set. Skipping hook call")
    if settings.CGW_AUTH_TOKEN is None:
        raise ValueError("CGW_AUTH_TOKEN is not set. Skipping hook call")
    return (settings.CGW_URL, settings.CGW_AUTH_TOKEN)


def hook_event(event: HookEvent) -> None:
    try:
        (url, token) = cgw_setup()
        url = urljoin(url.rstrip("/") + "/", "v1/hooks/events")
        post(url, token, json={"type": event.type, "chainId": str(event.chain_id)})
    except Exception as error:
        logger.error(error)


def post(url: str, token: str, json: Dict[str, Any]) -> None:
    request = setup_session().post(
        url,
        json=json,
        headers={"Authorization": f"Basic {token}"},
        timeout=settings.CGW_SESSION_TIMEOUT_SECONDS,
    )
    request.raise_for_status()
