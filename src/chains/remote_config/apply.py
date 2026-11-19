# SPDX-License-Identifier: FSL-1.1-MIT
"""Transactional, selective application of reconciliation changes.

Every change selected by the operator is applied inside a single
``transaction.atomic()`` block and recorded as a Django admin ``LogEntry`` so the
existing admin "History" surfaces who reconciled what.
"""
from collections.abc import Callable
from dataclasses import dataclass

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from django.db.models import Model

from ..models import Chain, Feature, Service
from .diff import SCOPE_PER_CHAIN, Change, ChangeType, FieldName


@dataclass
class ApplyResult:
    """Counts of each applied change type, plus changes skipped as stale."""

    added: int = 0
    attached: int = 0
    updated: int = 0
    detached: int = 0
    deleted: int = 0
    skipped: int = 0

    @property
    def total(self) -> int:
        return self.added + self.attached + self.updated + self.detached + self.deleted


def _log(actor: AbstractBaseUser, obj: Model, action_flag: int, message: str) -> None:
    """Write a Django admin audit LogEntry for a single object.

    Django 6 dropped ``log_action`` in favour of ``log_actions``; for deletions
    call this *before* deleting so the object still has a pk and repr.
    """
    LogEntry.objects.log_actions(
        actor.pk, [obj], action_flag, change_message=message, single_object=True
    )


def _chains(chain_ids: tuple[str, ...]) -> list[Chain]:
    numeric = [int(chain_id) for chain_id in chain_ids if chain_id.isdigit()]
    return list(Chain.objects.filter(pk__in=numeric))


def _get_or_create_service(change: Change) -> Service:
    service, _ = Service.objects.get_or_create(
        key=change.service_key, defaults={"name": change.service_key}
    )
    return service


def _existing_feature(change: Change) -> Feature | None:
    """Return the change's Feature, or None if it was deleted since the diff."""
    if change.feature_id is None:
        raise ValueError(f"{change.type.value} change for '{change.key}' has no feature_id")
    return Feature.objects.filter(pk=change.feature_id).first()


def _apply_deltas(feature: Feature, change: Change) -> None:
    """Apply only the deltas carried on ``change`` (operator-selected)."""
    dirty_fields: list[str] = []
    for delta in change.deltas:
        if delta.name is FieldName.DESCRIPTION:
            feature.description = str(delta.declared)
            dirty_fields.append("description")
        elif delta.name is FieldName.SCOPE:
            feature.scope = str(delta.declared)
            dirty_fields.append("scope")
        elif delta.name is FieldName.CHAINS:
            if not isinstance(delta.declared, tuple):
                raise TypeError(f"chains delta for '{change.key}' must be a tuple")
            feature.chains.set(_chains(delta.declared))
    if dirty_fields:
        feature.save(update_fields=dirty_fields)


def _apply_add(change: Change, actor: AbstractBaseUser, result: ApplyResult) -> None:
    service = _get_or_create_service(change)
    # A key declared by several services is proposed as ADD for each; the first
    # creates and seeds the row, the later ones only attach their service.
    feature, created = Feature.objects.get_or_create(
        key=change.key,
        defaults={
            "description": change.declared_description or "",
            "scope": change.declared_scope or Feature.Scope.PER_CHAIN,
        },
    )
    feature.services.add(service)
    if not created:
        _log(actor, feature, CHANGE, f"Attached service {change.service_key}")
        result.attached += 1
        return
    if feature.scope == SCOPE_PER_CHAIN and change.declared_chains:
        feature.chains.set(_chains(change.declared_chains))
    _log(actor, feature, ADDITION, f"Declared by {change.service_key}")
    result.added += 1


def _apply_attach(change: Change, actor: AbstractBaseUser, result: ApplyResult) -> None:
    feature = _existing_feature(change)
    if feature is None:
        result.skipped += 1
        return
    feature.services.add(_get_or_create_service(change))
    _apply_deltas(feature, change)
    _log(actor, feature, CHANGE, f"Attached service {change.service_key}")
    result.attached += 1


def _apply_update(change: Change, actor: AbstractBaseUser, result: ApplyResult) -> None:
    feature = _existing_feature(change)
    if feature is None:
        result.skipped += 1
        return
    _apply_deltas(feature, change)
    _log(actor, feature, CHANGE, f"Updated {', '.join(d.name.value for d in change.deltas)}")
    result.updated += 1


def _apply_detach(change: Change, actor: AbstractBaseUser, result: ApplyResult) -> None:
    feature = _existing_feature(change)
    service = Service.objects.filter(key=change.service_key).first()
    if feature is None or service is None:
        result.skipped += 1
        return
    feature.services.remove(service)
    _log(actor, feature, CHANGE, f"Detached service {change.service_key}")
    result.detached += 1


def _apply_delete(change: Change, actor: AbstractBaseUser, result: ApplyResult) -> None:
    feature = _existing_feature(change)
    if feature is None:
        result.skipped += 1
        return
    _log(actor, feature, DELETION, "Removed: no remaining services")
    feature.delete()
    result.deleted += 1


_APPLIERS: dict[ChangeType, Callable[[Change, AbstractBaseUser, ApplyResult], None]] = {
    ChangeType.ADD: _apply_add,
    ChangeType.ATTACH: _apply_attach,
    ChangeType.UPDATE: _apply_update,
    ChangeType.DETACH: _apply_detach,
    ChangeType.DELETE: _apply_delete,
}


@transaction.atomic
def apply_changes(changes: list[Change], actor: AbstractBaseUser) -> ApplyResult:
    """Apply the selected changes transactionally and write audit log entries.

    A change whose Feature (or, for DETACH, Service) no longer exists is counted
    as skipped: the page was computed before someone else changed the database.

    Args:
        changes: The exact changes the operator selected (already filtered to
            the chosen rows and, for UPDATE/ATTACH, the chosen field deltas).
        actor: The admin user performing the reconcile (for the audit log).

    Returns:
        An :class:`ApplyResult` with per-type counts.
    """
    result = ApplyResult()
    for change in changes:
        _APPLIERS[change.type](change, actor, result)
    return result
