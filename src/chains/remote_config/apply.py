# SPDX-License-Identifier: FSL-1.1-MIT
"""Transactional, selective application of reconciliation changes.

Every change selected by the operator is applied inside a single
``transaction.atomic()`` block and recorded as a Django admin ``LogEntry`` so the
existing admin "History" surfaces who reconciled what.
"""
from dataclasses import dataclass

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db import transaction
from django.db.models import Model

from ..models import Chain, Feature, Service
from .diff import SCOPE_PER_CHAIN, Change, ChangeType

Actor = AbstractBaseUser | AnonymousUser | None


@dataclass
class ApplyResult:
    """Counts of each applied change type."""

    added: int = 0
    attached: int = 0
    updated: int = 0
    detached: int = 0
    deleted: int = 0

    @property
    def total(self) -> int:
        return self.added + self.attached + self.updated + self.detached + self.deleted


def _log(actor: Actor, obj: Model, action_flag: int, message: str) -> None:
    """Write a Django admin audit LogEntry for a single object.

    Django 6 dropped ``log_action`` in favour of ``log_actions``; for deletions
    call this *before* deleting so the object still has a pk and repr.
    """
    if actor is None or actor.pk is None:
        return
    LogEntry.objects.log_actions(
        actor.pk, [obj], action_flag, change_message=message, single_object=True
    )


def _chains_queryset(chain_ids: tuple[str, ...]) -> list[Chain]:
    numeric = [int(chain_id) for chain_id in chain_ids if chain_id.isdigit()]
    return list(Chain.objects.filter(pk__in=numeric))


def _apply_deltas(feature: Feature, change: Change) -> None:
    """Apply only the deltas carried on ``change`` (operator-selected)."""
    dirty_fields: list[str] = []
    for delta in change.deltas:
        if delta.name == "description":
            feature.description = str(delta.declared)
            dirty_fields.append("description")
        elif delta.name == "scope":
            feature.scope = str(delta.declared)
            dirty_fields.append("scope")
        elif delta.name == "chains":
            declared = delta.declared
            assert isinstance(declared, tuple)
            feature.chains.set(_chains_queryset(declared))
    if dirty_fields:
        feature.save(update_fields=dirty_fields)


def _require_feature_id(change: Change) -> int:
    if change.feature_id is None:
        raise ValueError(f"{change.type.value} change for '{change.key}' has no feature_id")
    return change.feature_id


@transaction.atomic
def apply_changes(changes: list[Change], actor: Actor = None) -> ApplyResult:
    """Apply the selected changes transactionally and write audit log entries.

    Args:
        changes: The exact changes the operator selected (already filtered to
            the chosen rows and, for UPDATE/ATTACH, the chosen field deltas).
        actor: The admin user performing the reconcile (for the audit log).

    Returns:
        An :class:`ApplyResult` with per-type counts.
    """
    result = ApplyResult()

    for change in changes:
        if change.type is ChangeType.ADD:
            service, _ = Service.objects.get_or_create(
                key=change.service_key, defaults={"name": change.service_key}
            )
            # Idempotent: the same key may be declared by several services and
            # proposed as ADD for each (the per-service diff shares one DB
            # snapshot). The first ADD creates the row; later ADDs for the same
            # key just attach their service instead of colliding on the unique
            # key. Seeding (description/scope/chains) only happens on create.
            feature, created = Feature.objects.get_or_create(
                key=change.key,
                defaults={
                    "description": change.declared_description or "",
                    "scope": change.declared_scope or Feature.Scope.PER_CHAIN,
                },
            )
            feature.services.add(service)
            if created:
                if feature.scope == SCOPE_PER_CHAIN and change.declared_chains:
                    feature.chains.set(_chains_queryset(change.declared_chains))
                _log(actor, feature, ADDITION, f"Declared by {change.service_key}")
                result.added += 1
            else:
                _log(actor, feature, CHANGE, f"Attached service {change.service_key}")
                result.attached += 1

        elif change.type is ChangeType.ATTACH:
            service, _ = Service.objects.get_or_create(
                key=change.service_key, defaults={"name": change.service_key}
            )
            feature = Feature.objects.get(pk=_require_feature_id(change))
            feature.services.add(service)
            _apply_deltas(feature, change)
            _log(actor, feature, CHANGE, f"Attached service {change.service_key}")
            result.attached += 1

        elif change.type is ChangeType.UPDATE:
            feature = Feature.objects.get(pk=_require_feature_id(change))
            _apply_deltas(feature, change)
            _log(
                actor,
                feature,
                CHANGE,
                f"Updated {', '.join(d.name for d in change.deltas)}",
            )
            result.updated += 1

        elif change.type is ChangeType.DETACH:
            feature = Feature.objects.get(pk=_require_feature_id(change))
            try:
                service = Service.objects.get(key=change.service_key)
            except Service.DoesNotExist:
                continue
            feature.services.remove(service)
            _log(actor, feature, CHANGE, f"Detached service {change.service_key}")
            result.detached += 1

        elif change.type is ChangeType.DELETE:
            feature = Feature.objects.get(pk=_require_feature_id(change))
            _log(actor, feature, DELETION, "Removed: no remaining services")
            feature.delete()
            result.deleted += 1

    return result
