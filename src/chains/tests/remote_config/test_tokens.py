# SPDX-License-Identifier: FSL-1.1-MIT
"""Pure round-trip tests for change tokens (no Django required)."""
import base64
import json

import pytest

from chains.remote_config.diff import Change, ChangeType, FieldDelta, FieldName
from chains.remote_config.tokens import change_from_token, change_to_token


def test_round_trips_add_change() -> None:
    change = Change(
        type=ChangeType.ADD,
        service_key="WALLET_WEB",
        key="NEWFLAG",
        declared_description="A flag.",
        declared_scope="PER_CHAIN",
        declared_chains=("1", "100"),
    )
    assert change_from_token(change_to_token(change)) == change


def test_round_trips_update_with_authoritative_and_chain_deltas() -> None:
    change = Change(
        type=ChangeType.UPDATE,
        service_key="CGW",
        key="X",
        feature_id=42,
        deltas=(
            FieldDelta(FieldName.DESCRIPTION, "old", "new", True),
            FieldDelta(FieldName.CHAINS, ("1",), ("1", "10"), False),
        ),
    )
    restored = change_from_token(change_to_token(change))
    assert restored == change
    # chains deltas must come back as tuples (not lists) for apply().
    chains_delta = next(d for d in restored.deltas if d.name is FieldName.CHAINS)
    assert isinstance(chains_delta.declared, tuple)


def test_round_trips_delete_change() -> None:
    change = Change(
        type=ChangeType.DELETE,
        service_key="WALLET_WEB",
        key="DEAD",
        feature_id=7,
        remaining_services_after=0,
    )
    assert change_from_token(change_to_token(change)) == change


def test_invalid_token_raises_value_error() -> None:
    with pytest.raises(ValueError):
        change_from_token("@@not-base64@@")


def test_decodable_token_with_missing_fields_raises_value_error() -> None:
    token = base64.urlsafe_b64encode(json.dumps({"type": "DELETE"}).encode()).decode()

    with pytest.raises(ValueError, match="service_key"):
        change_from_token(token)


def test_token_with_unknown_field_name_raises_value_error() -> None:
    change = Change(
        type=ChangeType.UPDATE,
        service_key="CGW",
        key="X",
        feature_id=1,
        deltas=(FieldDelta(FieldName.SCOPE, "GLOBAL", "PER_CHAIN", True),),
    )
    payload = json.loads(base64.urlsafe_b64decode(change_to_token(change)))
    payload["deltas"][0]["name"] = "colour"
    token = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    with pytest.raises(ValueError):
        change_from_token(token)


def _token_with(**fields: object) -> str:
    change = Change(type=ChangeType.UPDATE, service_key="CGW", key="X", feature_id=1)
    payload = json.loads(base64.urlsafe_b64decode(change_to_token(change)))
    payload.update(fields)
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def _delta(name: str, current: object, declared: object) -> dict[str, object]:
    return {"name": name, "current": current, "declared": declared, "authoritative": False}


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"feature_id": "abc"}, "feature_id must be an integer"),
        ({"feature_id": True}, "feature_id must be an integer"),
        ({"feature_id": None}, "UPDATE change needs a feature_id"),
        ({"key": 7}, "key must be a string"),
        ({"declared_scope": "SOMETIMES"}, "declared_scope must be one of"),
        ({"declared_chains": "1"}, "declared_chains must be a list"),
        (
            {"deltas": [_delta("chains", [1], [])]},
            "delta current must be a string",
        ),
        (
            {"deltas": [_delta("scope", "GLOBAL", "X")]},
            "delta declared must be one of",
        ),
    ],
)
def test_token_with_a_wrong_field_type_raises_value_error(
    fields: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        change_from_token(_token_with(**fields))
