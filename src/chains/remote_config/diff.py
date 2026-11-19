# SPDX-License-Identifier: FSL-1.1-MIT
"""Pure diff engine comparing a declaration against database state.

No Django imports. Operates on plain value objects so it can be unit-tested in
isolation. The Django ``Feature``/``Service``/``Chain`` rows are projected into
:class:`FeatureState` objects by :mod:`chains.remote_config.state` before being
passed here.
"""
from dataclasses import dataclass, field
from enum import Enum

from .declaration import FeatureDecl

# Scope literals (mirror chains.models.Feature.Scope without importing Django).
SCOPE_GLOBAL = "GLOBAL"
SCOPE_PER_CHAIN = "PER_CHAIN"

DISABLED_WARNING = (
    "The code declares this flag with enabled: false. Applying removes it from this service."
)


class ChangeType(str, Enum):
    ADD = "ADD"  # key absent from DB entirely -> create Feature + attach service
    ATTACH = "ATTACH"  # Feature exists, service not attached -> attach service
    UPDATE = "UPDATE"  # attached, but description/scope/chains differ
    DETACH = "DETACH"  # in DB for this service, not declared -> detach service
    DELETE = "DELETE"  # detach would leave zero services -> offer row delete


class FieldName(str, Enum):
    DESCRIPTION = "description"
    SCOPE = "scope"
    CHAINS = "chains"


@dataclass(frozen=True)
class FieldDelta:
    """A single field that differs between declaration and database."""

    name: FieldName
    current: object
    declared: object
    # True: code is authoritative (description/scope). False: informational
    # (chains divergence is "release-default vs current", never force-applied).
    authoritative: bool


@dataclass(frozen=True)
class FeatureState:
    """Projection of a DB ``Feature`` row, decoupled from Django."""

    feature_id: int
    key: str
    description: str
    scope: str
    chains: frozenset[str]
    services: frozenset[str]


@dataclass(frozen=True)
class Change:
    """One proposed reconciliation action for a single feature key."""

    type: ChangeType
    service_key: str
    key: str
    feature_id: int | None = None
    declared_description: str | None = None
    declared_scope: str | None = None
    declared_chains: tuple[str, ...] = ()
    deltas: tuple[FieldDelta, ...] = ()
    remaining_services_after: int | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _seedable_chains(
    decl: FeatureDecl, known_chain_ids: set[str] | None
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split a declaration's defaultChains into (known, unknown) for PER_CHAIN.

    GLOBAL features ignore chains entirely. When ``known_chain_ids`` is None no
    filtering is applied (all declared chains are treated as known).
    """
    if decl.scope != SCOPE_PER_CHAIN:
        return (), ()
    if known_chain_ids is None:
        return decl.default_chains, ()
    known = tuple(c for c in decl.default_chains if c in known_chain_ids)
    unknown = tuple(c for c in decl.default_chains if c not in known_chain_ids)
    return known, unknown


def _unknown_chain_warning(unknown: tuple[str, ...]) -> tuple[str, ...]:
    if not unknown:
        return ()
    return (f"Unknown chain id(s) skipped: {', '.join(unknown)}",)


def _field_deltas(
    decl: FeatureDecl, state: FeatureState, known_chain_ids: set[str] | None
) -> tuple[FieldDelta, ...]:
    """Compute the fields that differ between a declaration and DB state."""
    deltas: list[FieldDelta] = []

    if decl.description != state.description:
        deltas.append(
            FieldDelta(
                FieldName.DESCRIPTION, state.description, decl.description, True
            )
        )

    if decl.scope != state.scope:
        deltas.append(FieldDelta(FieldName.SCOPE, state.scope, decl.scope, True))

    if decl.scope == SCOPE_PER_CHAIN:
        known, _ = _seedable_chains(decl, known_chain_ids)
        declared_set = set(known)
        if declared_set != set(state.chains):
            deltas.append(
                FieldDelta(
                    FieldName.CHAINS,
                    tuple(sorted(state.chains, key=_chain_sort_key)),
                    tuple(sorted(declared_set, key=_chain_sort_key)),
                    False,
                )
            )

    return tuple(deltas)


def _chain_sort_key(chain_id: str) -> tuple[int, str]:
    """Sort numeric chain ids numerically, with a stable fallback."""
    return (int(chain_id), chain_id) if chain_id.isdigit() else (1 << 62, chain_id)


def _declared_change(
    service_key: str,
    decl: FeatureDecl,
    existing: FeatureState | None,
    known_chain_ids: set[str] | None,
) -> Change | None:
    """Return the ADD/ATTACH/UPDATE change for one declared key, or None if in sync."""
    change_type: ChangeType
    feature_id: int | None = None
    deltas: tuple[FieldDelta, ...] = ()
    if existing is None:
        change_type = ChangeType.ADD
    else:
        deltas = _field_deltas(decl, existing, known_chain_ids)
        feature_id = existing.feature_id
        if service_key not in existing.services:
            change_type = ChangeType.ATTACH
        elif deltas:
            change_type = ChangeType.UPDATE
        else:
            return None

    known, unknown = _seedable_chains(decl, known_chain_ids)
    return Change(
        type=change_type,
        service_key=service_key,
        key=decl.key,
        feature_id=feature_id,
        declared_description=decl.description,
        declared_scope=decl.scope,
        declared_chains=known,
        deltas=deltas,
        warnings=_unknown_chain_warning(unknown),
    )


def diff_service(
    service_key: str,
    declared: tuple[FeatureDecl, ...] | list[FeatureDecl],
    all_states: dict[str, FeatureState],
    known_chain_ids: set[str] | None = None,
) -> list[Change]:
    """Diff one service's declaration against the database.

    Args:
        service_key: The owning service key (e.g. ``WALLET_WEB``).
        declared: Declared features for this service. A feature with
            ``enabled=False`` is treated as undeclared: no ADD, and an existing
            row for this service gets a removal with a warning.
        all_states: Every DB feature keyed by ``key`` (any service), used to
            distinguish ADD (no row) from ATTACH (row exists, other service).
        known_chain_ids: All chain ids known to the DB. When provided,
            defaultChains referencing absent chains are skipped with a warning.

    Returns:
        The list of proposed :class:`Change` actions, in a stable order
        (declared keys first in declaration order, then removals sorted by key).
    """
    changes: list[Change] = []
    enabled = [d for d in declared if d.enabled]
    enabled_keys = {d.key for d in enabled}
    disabled_keys = {d.key for d in declared if not d.enabled}

    for decl in enabled:
        change = _declared_change(service_key, decl, all_states.get(decl.key), known_chain_ids)
        if change is not None:
            changes.append(change)

    for key in sorted(all_states):
        state = all_states[key]
        if service_key in state.services and key not in enabled_keys:
            remaining = len(state.services - {service_key})
            change_type = ChangeType.DETACH if remaining else ChangeType.DELETE
            warnings = (DISABLED_WARNING,) if key in disabled_keys else ()
            changes.append(
                Change(
                    type=change_type,
                    service_key=service_key,
                    key=key,
                    feature_id=state.feature_id,
                    remaining_services_after=remaining,
                    warnings=warnings,
                )
            )

    return changes
