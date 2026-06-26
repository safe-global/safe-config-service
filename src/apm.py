# SPDX-License-Identifier: FSL-1.1-MIT
import logging
import os
from contextlib import AbstractContextManager, nullcontext
from typing import Any

logger = logging.getLogger(__name__)

ENABLED = os.environ.get("DD_APM_ENABLED", "false").lower() == "true"


def setup_tracing() -> None:
    """Initialize ddtrace integrations. Must be called before any Django import."""
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
    """Return a ddtrace span context manager, or a no-op when APM is disabled."""
    if not ENABLED:
        return nullcontext()
    from ddtrace import tracer

    kwargs: dict[str, str] = {}
    if service:
        kwargs["service"] = service
    if resource:
        kwargs["resource"] = resource
    return tracer.trace(operation_name, **kwargs)  # type: ignore[return-value]
