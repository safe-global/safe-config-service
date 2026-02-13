import logging
from collections.abc import Iterable

from clients.safe_client_gateway import HookEvent, hook_event

logger = logging.getLogger(__name__)


class ChainUpdateWebhookService:
    def notify(
        self,
        chain_ids: Iterable[int],
        service_keys: list[str] | None = None,
    ) -> None:
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
                    HookEvent(type=HookEvent.Type.CHAIN_UPDATE, chain_id=chain_id)
                )
