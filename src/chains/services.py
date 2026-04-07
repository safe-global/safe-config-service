# SPDX-License-Identifier: FSL-1.1-MIT
import logging
from collections.abc import Iterable

from chains.models import Service
from clients.safe_client_gateway import HookEvent, hook_event

logger = logging.getLogger(__name__)


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

        for chain_id in chain_ids:
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
                hook_event(
                    HookEvent(
                        type=HookEvent.Type.CHAIN_UPDATE,
                        chain_id=chain_id,
                    )
                )
