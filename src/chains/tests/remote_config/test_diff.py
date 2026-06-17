# SPDX-License-Identifier: FSL-1.1-MIT
"""Pure unit tests for the diff engine (no Django required)."""
from chains.remote_config.declaration import FeatureDecl
from chains.remote_config.diff import (
    Change,
    ChangeType,
    FeatureState,
    diff_service,
)

WEB = "WALLET_WEB"
CGW = "CGW"


def _state(
    key: str,
    *,
    feature_id: int = 1,
    description: str = "desc",
    scope: str = "PER_CHAIN",
    chains: set[str] | None = None,
    services: set[str] | None = None,
) -> FeatureState:
    return FeatureState(
        feature_id=feature_id,
        key=key,
        description=description,
        scope=scope,
        chains=frozenset(chains or set()),
        services=frozenset(services or {WEB}),
    )


def _decl(
    key: str,
    *,
    description: str = "desc",
    scope: str = "PER_CHAIN",
    default_chains: tuple[str, ...] = (),
) -> FeatureDecl:
    return FeatureDecl(key, description, scope, default_chains)


def test_add_new_global() -> None:
    changes = diff_service(WEB, [_decl("NEW", scope="GLOBAL")], {})
    assert len(changes) == 1
    assert changes[0].type is ChangeType.ADD
    assert changes[0].declared_scope == "GLOBAL"
    assert changes[0].declared_chains == ()
    assert changes[0].feature_id is None


def test_add_new_per_chain_seeds_known_chains() -> None:
    changes = diff_service(
        WEB,
        [_decl("NEW", scope="PER_CHAIN", default_chains=("1", "100"))],
        {},
        known_chain_ids={"1", "100"},
    )
    assert changes[0].type is ChangeType.ADD
    assert set(changes[0].declared_chains) == {"1", "100"}
    assert changes[0].warnings == ()


def test_add_skips_unknown_chain_with_warning() -> None:
    changes = diff_service(
        WEB,
        [_decl("NEW", scope="PER_CHAIN", default_chains=("1", "999999"))],
        {},
        known_chain_ids={"1"},
    )
    assert changes[0].declared_chains == ("1",)
    assert changes[0].warnings
    assert "999999" in changes[0].warnings[0]


def test_attach_when_feature_exists_for_other_service() -> None:
    states = {"SHARED": _state("SHARED", feature_id=7, services={CGW})}
    changes = diff_service(WEB, [_decl("SHARED")], states)
    assert len(changes) == 1
    assert changes[0].type is ChangeType.ATTACH
    assert changes[0].service_key == WEB
    assert changes[0].feature_id == 7


def test_update_description_is_authoritative() -> None:
    states = {"X": _state("X", description="old", services={WEB})}
    changes = diff_service(WEB, [_decl("X", description="new")], states)
    assert len(changes) == 1
    assert changes[0].type is ChangeType.UPDATE
    delta = next(d for d in changes[0].deltas if d.name == "description")
    assert delta.current == "old"
    assert delta.declared == "new"
    assert delta.authoritative is True


def test_update_scope_is_authoritative() -> None:
    states = {"X": _state("X", scope="PER_CHAIN", services={WEB})}
    changes = diff_service(WEB, [_decl("X", scope="GLOBAL")], states)
    delta = next(d for d in changes[0].deltas if d.name == "scope")
    assert delta.authoritative is True
    assert delta.current == "PER_CHAIN"
    assert delta.declared == "GLOBAL"


def test_update_chains_only_is_non_authoritative() -> None:
    states = {"X": _state("X", chains={"1"}, services={WEB})}
    changes = diff_service(
        WEB,
        [_decl("X", default_chains=("1", "10"))],
        states,
        known_chain_ids={"1", "10"},
    )
    assert changes[0].type is ChangeType.UPDATE
    delta = next(d for d in changes[0].deltas if d.name == "chains")
    assert delta.authoritative is False
    assert delta.current == ("1",)
    assert delta.declared == ("1", "10")


def test_no_change_when_declaration_matches_db() -> None:
    states = {"X": _state("X", description="desc", chains={"1"}, services={WEB})}
    changes = diff_service(
        WEB, [_decl("X", default_chains=("1",))], states, known_chain_ids={"1"}
    )
    assert changes == []


def test_detach_when_multi_service() -> None:
    states = {"X": _state("X", feature_id=3, services={WEB, CGW})}
    changes = diff_service(WEB, [], states)
    assert len(changes) == 1
    assert changes[0].type is ChangeType.DETACH
    assert changes[0].remaining_services_after == 1
    assert changes[0].feature_id == 3


def test_delete_when_last_service() -> None:
    states = {"X": _state("X", feature_id=3, services={WEB})}
    changes = diff_service(WEB, [], states)
    assert changes[0].type is ChangeType.DELETE
    assert changes[0].remaining_services_after == 0


def test_removal_ignores_features_of_other_services() -> None:
    states = {"OTHER": _state("OTHER", services={CGW})}
    changes = diff_service(WEB, [], states)
    assert changes == []


def test_global_feature_ignores_chains_in_diff() -> None:
    states = {"G": _state("G", scope="GLOBAL", chains=set(), services={WEB})}
    # Declared GLOBAL with no chains -> no delta even though state has none.
    changes = diff_service(WEB, [_decl("G", scope="GLOBAL")], states)
    assert changes == []


def test_unknown_chain_ids_none_means_no_filtering() -> None:
    changes = diff_service(
        WEB,
        [_decl("NEW", scope="PER_CHAIN", default_chains=("1", "999999"))],
        {},
        known_chain_ids=None,
    )
    assert set(changes[0].declared_chains) == {"1", "999999"}
    assert changes[0].warnings == ()


def test_change_ordering_declared_first_then_removals() -> None:
    states = {
        "ZEBRA": _state("ZEBRA", feature_id=1, services={WEB}),
        "ALPHA": _state("ALPHA", feature_id=2, services={WEB}),
    }
    changes = diff_service(WEB, [_decl("NEW", scope="GLOBAL")], states)
    # New declared key first (ADD), then removals sorted by key (ALPHA, ZEBRA).
    assert [c.type for c in changes] == [
        ChangeType.ADD,
        ChangeType.DELETE,
        ChangeType.DELETE,
    ]
    assert [c.key for c in changes] == ["NEW", "ALPHA", "ZEBRA"]
