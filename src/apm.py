# SPDX-License-Identifier: FSL-1.1-MIT
import logging
import os
from contextlib import AbstractContextManager, nullcontext
from typing import Any

logger = logging.getLogger(__name__)

# Accepts the same truthy values as the repo's _parse_bool (gunicorn.py).
# Evaluated once at import time — tests that toggle DD_APM_ENABLED must
# reload this module (importlib.reload(apm)) to see the change.
_TRUTHY = frozenset({"y", "yes", "t", "true", "on", "1"})
ENABLED = os.environ.get("DD_APM_ENABLED", "false").lower() in _TRUTHY


def setup_tracing() -> None:
    """Initialize ddtrace integrations. Must be called before any Django import.

    Wired into wsgi.py only (WSGI/gunicorn deployment target). Management
    commands do not call this, so APM spans from ``manage.py`` commands will
    lack Django/requests/psycopg patches.
    """
    if not ENABLED:
        return
    from ddtrace import patch

    patch(
        django=True,
        requests=True,
        psycopg=True,
    )
    logger.info("Datadog APM initialized: django, requests, psycopg")


def trace(
    operation_name: str,
    service: str | None = None,
    resource: str | None = None,
) -> AbstractContextManager[Any]:
    """Return a ddtrace span context manager, or a no-op when APM is disabled.

    Never raises: any ddtrace initialisation error falls back to nullcontext()
    so call-sites cannot be broken by APM failures.
    """
    if not ENABLED:
        return nullcontext()
    try:
        from ddtrace.trace import tracer

        kwargs: dict[str, str] = {}
        if service:
            kwargs["service"] = service
        if resource:
            kwargs["resource"] = resource
        return tracer.trace(operation_name, **kwargs)
    except Exception:
        logger.warning("APM trace() unavailable, falling back to no-op", exc_info=True)
        return nullcontext()
