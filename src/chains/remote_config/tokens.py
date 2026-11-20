# SPDX-License-Identifier: FSL-1.1-MIT
"""Serialize a :class:`Change` to/from an opaque form token.

Used by the admin reconcile view to round-trip selected changes through the
POST without re-fetching. Pure (stdlib only).
"""
import base64
import json
from collections.abc import Sequence
from typing import Any, cast

from .diff import SCOPE_GLOBAL, SCOPE_PER_CHAIN, Change, ChangeType, FieldDelta, FieldName


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


_SCOPES = (SCOPE_GLOBAL, SCOPE_PER_CHAIN)


def _str(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string, got {value!r}")
    return value


def _optional_str(value: Any, field: str) -> str | None:
    return None if value is None else _str(value, field)


def _optional_int(value: Any, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer, got {value!r}")
    return value


def _str_tuple(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list, got {value!r}")
    return tuple(_str(item, field) for item in value)


def _scope(value: Any, field: str) -> str:
    if value not in _SCOPES:
        raise ValueError(f"{field} must be one of {_SCOPES}, got {value!r}")
    return str(value)


def _delta_value(name: FieldName, value: Any, field: str) -> object:
    if name is FieldName.CHAINS:
        return _str_tuple(value, field)
    if name is FieldName.SCOPE:
        return _scope(value, field)
    return _str(value, field)


def _delta_from_dict(data: Any) -> FieldDelta:
    if not isinstance(data, dict):
        raise ValueError(f"delta must be an object, got {data!r}")
    name = FieldName(data["name"])
    current = _delta_value(name, data["current"], "delta current")
    declared = _delta_value(name, data["declared"], "delta declared")
    if not isinstance(data["authoritative"], bool):
        raise ValueError("delta authoritative must be a boolean")
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
        if not isinstance(payload, dict):
            raise ValueError("token payload must be an object")
        change_type = ChangeType(payload["type"])
        service_key = _str(payload["service_key"], "service_key")
        key = _str(payload["key"], "key")
        feature_id = _optional_int(payload["feature_id"], "feature_id")
        if change_type is not ChangeType.ADD and feature_id is None:
            raise ValueError(f"{change_type.value} change needs a feature_id")
        declared_scope = payload["declared_scope"]
        if not isinstance(payload["deltas"], list):
            raise ValueError("deltas must be a list")
        return Change(
            type=change_type,
            service_key=service_key,
            key=key,
            feature_id=feature_id,
            declared_description=_optional_str(
                payload["declared_description"], "declared_description"
            ),
            declared_scope=None
            if declared_scope is None
            else _scope(declared_scope, "declared_scope"),
            declared_chains=_str_tuple(payload["declared_chains"], "declared_chains"),
            deltas=tuple(_delta_from_dict(delta) for delta in payload["deltas"]),
            remaining_services_after=_optional_int(
                payload["remaining_services_after"], "remaining_services_after"
            ),
        )
    except (ValueError, KeyError, TypeError) as error:
        raise ValueError(f"Invalid change token: {error!r}") from error
