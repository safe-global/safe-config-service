# SPDX-License-Identifier: FSL-1.1-MIT
"""Serialize a :class:`Change` to/from an opaque form token.

Used by the admin reconcile view to round-trip selected changes through the
POST without re-fetching. Pure (stdlib only).
"""
import base64
import json
from collections.abc import Sequence
from typing import Any, cast

from .diff import Change, ChangeType, FieldDelta, FieldName


def _encode_value(name: FieldName, value: object) -> Any:
    if name is FieldName.CHAINS:
        return list(cast(Sequence[str], value))
    return value


def _delta_to_dict(delta: FieldDelta) -> dict[str, Any]:
    return {
        "name": delta.name.value,
        "current": _encode_value(delta.name, delta.current),
        "declared": _encode_value(delta.name, delta.declared),
        "authoritative": delta.authoritative,
    }


def _delta_from_dict(data: dict[str, Any]) -> FieldDelta:
    name = FieldName(data["name"])
    is_chains = name is FieldName.CHAINS
    current = tuple(data["current"]) if is_chains else data["current"]
    declared = tuple(data["declared"]) if is_chains else data["declared"]
    return FieldDelta(name, current, declared, data["authoritative"])


def change_to_token(change: Change) -> str:
    """Encode ``change`` as a URL-safe base64 JSON token."""
    payload = {
        "type": change.type.value,
        "service_key": change.service_key,
        "key": change.key,
        "feature_id": change.feature_id,
        "declared_description": change.declared_description,
        "declared_scope": change.declared_scope,
        "declared_chains": list(change.declared_chains),
        "deltas": [_delta_to_dict(delta) for delta in change.deltas],
        "remaining_services_after": change.remaining_services_after,
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode()


def change_from_token(token: str) -> Change:
    """Decode a token produced by :func:`change_to_token`.

    Raises:
        ValueError: If the token is malformed or not decodable.
    """
    try:
        payload = json.loads(base64.urlsafe_b64decode(token.encode()))
        return Change(
            type=ChangeType(payload["type"]),
            service_key=payload["service_key"],
            key=payload["key"],
            feature_id=payload["feature_id"],
            declared_description=payload["declared_description"],
            declared_scope=payload["declared_scope"],
            declared_chains=tuple(payload["declared_chains"]),
            deltas=tuple(_delta_from_dict(delta) for delta in payload["deltas"]),
            remaining_services_after=payload["remaining_services_after"],
        )
    except (ValueError, KeyError, TypeError) as error:
        raise ValueError(f"Invalid change token: {error!r}") from error
