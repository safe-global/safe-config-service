# SPDX-License-Identifier: FSL-1.1-MIT
"""Build a remote-config declaration document from current database state.

Shared by the ``export_remote_config`` management command and the admin
"Export declaration" view.
"""
from typing import Any

from ..models import Feature, Service


class ServiceNotFound(Exception):
    """No ``Service`` row exists for the requested key."""


def build_declaration_document(service_key: str) -> dict[str, Any]:
    """Return the declaration JSON for ``service_key`` from current DB state.

    Features are ordered by key; ``defaultChains`` holds the numerically-sorted
    enabled chain ids for PER_CHAIN features and is empty for GLOBAL ones.

    Raises:
        ServiceNotFound: If no ``Service`` with that key exists.
    """
    try:
        service = Service.objects.get(key=service_key)
    except Service.DoesNotExist as error:
        raise ServiceNotFound(service_key) from error

    features = (
        Feature.objects.filter(services=service)
        .prefetch_related("chains")
        .order_by("key")
    )

    entries = []
    for feature in features:
        if feature.scope == Feature.Scope.PER_CHAIN:
            default_chains = sorted(
                (str(chain.id) for chain in feature.chains.all()), key=int
            )
        else:
            default_chains = []
        entries.append(
            {
                "key": feature.key,
                "description": feature.description,
                "scope": feature.scope,
                "defaultChains": default_chains,
            }
        )

    return {
        "$schema": "./remote-config.schema.json",
        "service": service_key,
        "features": entries,
    }
