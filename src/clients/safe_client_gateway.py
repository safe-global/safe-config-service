# SPDX-License-Identifier: FSL-1.1-MIT
import logging
from dataclasses import dataclass
from enum import Enum
from functools import cache
from typing import Any, Dict
from urllib.parse import urljoin

import apm
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
    service: str | None = None


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
        with apm.trace("cgw.hook_event", resource=event.type.value) as span:
            if span is not None:
                span.set_tag("cgw.chain_id", str(event.chain_id))
                if event.service:
                    span.set_tag("cgw.service", event.service)
            try:
                (url, token) = cgw_setup()
                url = urljoin(url.rstrip("/") + "/", "v1/hooks/events")
                payload: Dict[str, Any] = {"type": event.type, "chainId": str(event.chain_id)}
                if event.service is not None:
                    payload["service"] = event.service
                post(url, token, json=payload)
            except Exception as error:
                if span is not None:
                    span.set_exc_info(type(error), error, error.__traceback__)
                logger.error(error)
    except Exception:
        logger.exception("APM instrumentation error in hook_event")


def post(url: str, token: str, json: Dict[str, Any]) -> None:
    request = setup_session().post(
        url,
        json=json,
        headers={"Authorization": f"Basic {token}"},
        timeout=settings.CGW_SESSION_TIMEOUT_SECONDS,
    )
    request.raise_for_status()
