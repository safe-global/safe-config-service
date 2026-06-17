# SPDX-License-Identifier: FSL-1.1-MIT
"""Pure round-trip tests for change tokens (no Django required)."""
import pytest

from chains.remote_config.diff import Change, ChangeType, FieldDelta
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
            FieldDelta("description", "old", "new", True),
            FieldDelta("chains", ("1",), ("1", "10"), False),
        ),
    )
    restored = change_from_token(change_to_token(change))
    assert restored == change
    # chains deltas must come back as tuples (not lists) for apply().
    chains_delta = next(d for d in restored.deltas if d.name == "chains")
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
