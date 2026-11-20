# SPDX-License-Identifier: FSL-1.1-MIT
import logging
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from django.db import transaction

from chains.models import Service
from clients.safe_client_gateway import HookEvent, hook_event

logger = logging.getLogger(__name__)

_pending_hooks: ContextVar[set[tuple[int, str | None]] | None] = ContextVar(
    "pending_chain_update_hooks", default=None
)


@contextmanager
def batched_chain_updates() -> Iterator[None]:
    """Collect CHAIN_UPDATE hooks and send each (chain, service) pair once after commit.

    Use inside ``transaction.atomic()``: the hooks are sent only if the
    transaction commits, so CGW never re-fetches data that is not yet visible.
    """
    pending: set[tuple[int, str | None]] = set()
    token = _pending_hooks.set(pending)
    try:
        yield
    finally:
        _pending_hooks.reset(token)
    transaction.on_commit(lambda: _send(sorted(pending, key=lambda p: (p[0], p[1] or ""))))


def _send(pairs: Iterable[tuple[int, str | None]]) -> None:
    for chain_id, service_key in pairs:
        hook_event(
            HookEvent(
                type=HookEvent.Type.CHAIN_UPDATE,
                chain_id=chain_id,
                service=service_key,
            )
        )


class ChainUpdateWebhookService:
    def notify(
        self,
        chain_ids: Iterable[int],
        service_keys: list[str] | None = None,
    ) -> None:
        """Send CHAIN_UPDATE hook events for the given chains.

        Args:
            chain_ids: Chain IDs to notify about.
            service_keys: Controls which services are notified:
                - None: query all registered Service records (broadcast).
                - []: no services — fire one hook per chain with service=None.
                - ["WALLET_WEB", ...]: fire one hook per (chain, service_key) pair.

        Inside :func:`batched_chain_updates` the hooks wait for the commit.
        """
        if service_keys is None:
            service_keys = list(
                Service.objects.values_list("key", flat=True)
            )
            if service_keys:
                logger.info(
                    "Broadcasting CHAIN_UPDATE to all %d services",
                    len(service_keys),
                )

        services: list[str | None] = list(service_keys) if service_keys else [None]
        pairs = [(chain_id, service_key) for chain_id in chain_ids for service_key in services]
        pending = _pending_hooks.get()
        if pending is not None:
            pending.update(pairs)
            return
        _send(pairs)
