# SPDX-License-Identifier: FSL-1.1-MIT
"""Admin "Reconcile flags" view: diff declarations at a ref vs the DB and apply.

Mixed into ``FeatureAdmin`` via :class:`ReconcileAdminMixin`. Standard Django
admin extension (``get_urls`` + ``TemplateResponse``), following the existing
``change_form.html`` customization style.
"""
import json
from collections import defaultdict
from dataclasses import dataclass, replace
from typing import Any, assert_never

from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from .models import Feature, RemoteConfigReconcileRef, Service
from .remote_config.apply import apply_changes
from .remote_config.declaration import (
    Declaration,
    DeclarationError,
    parse_declaration_text,
)
from .remote_config.diff import Change, ChangeType, FieldDelta, diff_service
from .remote_config.export import (
    ServiceNotFound,
    blank_description_keys,
    build_declaration_document,
)
from .remote_config.github import DeclarationFetchError, fetch_declaration_text
from .remote_config.sources import RemoteConfigSource, get_sources
from .remote_config.state import known_chain_ids, load_feature_states
from .remote_config.tokens import change_from_token, change_to_token


def _export_service_keys() -> list[str]:
    """Service keys offered in the export picker: configured ∪ those in the DB."""
    configured = {source.service_key for source in get_sources()}
    existing = set(Service.objects.values_list("key", flat=True))
    return sorted(configured | existing)


@dataclass
class ApplyUnit:
    """A single checkbox in the diff table: one applyable change."""

    token: str
    label: str
    detail: str
    default_checked: bool
    warnings: tuple[str, ...]


@dataclass
class SourceResult:
    """The diff outcome for one declaration source."""

    source: RemoteConfigSource
    ref: str
    units: list[ApplyUnit]
    error: str | None
    service_exists: bool
    warnings: list[str]


def _update_unit(
    change: Change,
    deltas: tuple[FieldDelta, ...],
    label: str,
    checked: bool,
    warnings: tuple[str, ...] = (),
) -> ApplyUnit:
    """Build one checkbox that applies ``deltas`` to an existing Feature."""
    unit_change = Change(
        type=ChangeType.UPDATE,
        service_key=change.service_key,
        key=change.key,
        feature_id=change.feature_id,
        deltas=deltas,
    )
    detail = "; ".join(f"{d.name.value}: {d.current!r} → {d.declared!r}" for d in deltas)
    return ApplyUnit(change_to_token(unit_change), label, detail, checked, warnings)


def _delta_units(change: Change, conflicted_fields: frozenset[str]) -> list[ApplyUnit]:
    """Split a change's field deltas into checkbox units.

    Authoritative (description/scope) deltas are pre-checked and grouped — unless
    the field conflicts across services (the same key declared with a different
    value elsewhere). A conflicting field is a code bug, not a DB drift, so it is
    a separate un-checked unit with a warning to avoid a flip-flop. Informational
    (chains) deltas are a separate, un-checked unit.
    """
    units: list[ApplyUnit] = []
    authoritative = tuple(
        d for d in change.deltas if d.authoritative and d.name not in conflicted_fields
    )
    conflicting = tuple(
        d for d in change.deltas if d.authoritative and d.name in conflicted_fields
    )
    informational = tuple(d for d in change.deltas if not d.authoritative)

    if authoritative:
        units.append(_update_unit(change, authoritative, f"UPDATE {change.key}", True))

    for delta in conflicting:
        name = delta.name.value
        warning = (
            f"'{change.key}' is declared with a different {name} by another "
            f"service. A shared feature has one {name}; align the declarations "
            f"in code rather than applying (applying flip-flops between services).",
        )
        label = f"UPDATE {change.key} ({name}, conflicting)"
        units.append(_update_unit(change, (delta,), label, False, warning))

    if informational:
        names = ", ".join(d.name.value for d in informational)
        label = f"UPDATE {change.key} {names} (release default)"
        units.append(_update_unit(change, informational, label, False))
    return units


def units_for_change(
    change: Change, conflicted_fields: frozenset[str] = frozenset()
) -> list[ApplyUnit]:
    """Expand a :class:`Change` into one or more checkbox units.

    ``conflicted_fields`` names Feature-level fields (description/scope) that the
    same key declares differently across services; such deltas are presented
    un-checked with a warning instead of pre-checked.
    """
    if change.type is ChangeType.ADD:
        detail = f"scope={change.declared_scope}"
        if change.declared_chains:
            detail += f", chains={', '.join(change.declared_chains)}"
        warnings = change.warnings
        if conflicted_fields:
            names = " and ".join(sorted(conflicted_fields))
            warnings += (
                f"Another service declares '{change.key}' with a different {names}. "
                f"The first applied ADD sets it for all services; align the declarations "
                f"in code before applying.",
            )
        return [
            ApplyUnit(
                change_to_token(change),
                f"ADD {change.key}",
                detail,
                not conflicted_fields,
                warnings,
            )
        ]

    if change.type is ChangeType.ATTACH:
        attach_only = replace(change, deltas=())
        units = [
            ApplyUnit(
                change_to_token(attach_only),
                f"ATTACH {change.key} → {change.service_key}",
                "",
                True,
                change.warnings,
            )
        ]
        units.extend(_delta_units(change, conflicted_fields))
        return units

    if change.type is ChangeType.UPDATE:
        return _delta_units(change, conflicted_fields)

    if change.type is ChangeType.DETACH:
        return [
            ApplyUnit(
                change_to_token(change),
                f"DETACH {change.key} from {change.service_key}",
                f"remaining services: {change.remaining_services_after}",
                False,
                change.warnings,
            )
        ]

    if change.type is ChangeType.DELETE:
        return [
            ApplyUnit(
                change_to_token(change),
                f"DELETE {change.key}",
                "no remaining services",
                False,
                change.warnings,
            )
        ]

    assert_never(change.type)


# Beyond chains.change_feature, which the view itself requires.
_REQUIRED_PERMISSIONS: dict[ChangeType, tuple[str, ...]] = {
    ChangeType.ADD: ("chains.add_feature",),
    ChangeType.ATTACH: (),
    ChangeType.UPDATE: (),
    # A DETACH deletes the row when it removes the last service.
    ChangeType.DETACH: ("chains.delete_feature",),
    ChangeType.DELETE: ("chains.delete_feature",),
}


def _missing_permissions(user: User, changes: list[Change]) -> set[str]:
    """Return the permissions the selected changes need that ``user`` does not have."""
    existing_services = set(Service.objects.values_list("key", flat=True))
    required: set[str] = set()
    for change in changes:
        required.update(_REQUIRED_PERMISSIONS[change.type])
        adds_service = change.type in (ChangeType.ADD, ChangeType.ATTACH)
        if adds_service and change.service_key not in existing_services:
            required.add("chains.add_service")
    return {permission for permission in required if not user.has_perm(permission)}


def _cross_source_conflicts(
    parsed: dict[str, Declaration],
) -> dict[str, frozenset[str]]:
    """Find keys declared by multiple sources with differing Feature-level fields.

    ``description`` and ``scope`` are columns on the single ``Feature`` row (the
    key is unique), so all services declaring a shared key must agree on them.
    Returns ``key -> {conflicting field names}``.
    """
    descriptions: dict[str, set[str]] = defaultdict(set)
    scopes: dict[str, set[str]] = defaultdict(set)
    for declaration in parsed.values():
        for feature in declaration.enabled_features():
            descriptions[feature.key].add(feature.description)
            scopes[feature.key].add(feature.scope)

    conflicts: dict[str, frozenset[str]] = {}
    for key, values in descriptions.items():
        fields = set()
        if len(values) > 1:
            fields.add("description")
        if len(scopes[key]) > 1:
            fields.add("scope")
        if fields:
            conflicts[key] = frozenset(fields)
    return conflicts


def build_source_results(refs: dict[str, str]) -> list[SourceResult]:
    """Fetch + diff every configured source at its ref. Errors are per-source.

    All declarations are fetched first so cross-source field conflicts (a shared
    key declared with a different description/scope) can be detected and surfaced.
    """
    states = load_feature_states()
    chain_ids = known_chain_ids()
    existing_services = set(Service.objects.values_list("key", flat=True))
    sources = get_sources()

    parsed: dict[str, Declaration] = {}
    errors: dict[str, str] = {}
    refs_used: dict[str, str] = {}
    for source in sources:
        ref = refs.get(source.service_key) or source.default_ref
        refs_used[source.service_key] = ref
        try:
            parsed[source.service_key] = parse_declaration_text(
                fetch_declaration_text(source.repo, ref, source.path)
            )
        except (DeclarationFetchError, DeclarationError) as error:
            errors[source.service_key] = str(error)

    conflicts = _cross_source_conflicts(parsed)
    results: list[SourceResult] = []

    for source in sources:
        ref = refs_used[source.service_key]
        service_exists = source.service_key in existing_services
        if source.service_key in errors:
            results.append(
                SourceResult(source, ref, [], errors[source.service_key], service_exists, [])
            )
            continue

        declaration = parsed[source.service_key]
        warnings: list[str] = []
        if declaration.service != source.service_key:
            warnings.append(
                f"Declared service '{declaration.service}' does not match configured "
                f"'{source.service_key}'; diffing against '{source.service_key}'."
            )
        enabled_keys = {feature.key for feature in declaration.enabled_features()}
        for key in sorted(enabled_keys & conflicts.keys()):
            fields = ", ".join(sorted(conflicts[key]))
            warnings.append(
                f"'{key}' is declared with a different {fields} by another service; "
                f"a shared feature has a single {fields}. Align the declarations in code."
            )

        changes = diff_service(
            source.service_key, declaration.features, states, chain_ids
        )
        units = [
            unit
            for change in changes
            for unit in units_for_change(change, conflicts.get(change.key, frozenset()))
        ]
        results.append(
            SourceResult(source, ref, units, None, service_exists, warnings)
        )
    return results


def _last_refs() -> dict[str, str]:
    return {r.service_key: r.ref for r in RemoteConfigReconcileRef.objects.all()}


class ReconcileForm(forms.Form):
    """One Git-ref input per declaration source, pre-filled with the last ref."""

    def __init__(
        self,
        sources: list[RemoteConfigSource],
        *args: Any,
        drift: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._sources = sources
        prefill = _last_refs()
        for source in sources:
            initial = source.default_ref if drift else prefill.get(
                source.service_key, source.default_ref
            )
            self.fields[f"ref_{source.service_key}"] = forms.CharField(
                label=f"{source.label} ({source.service_key})",
                initial=initial,
                required=True,
                help_text=f"{source.repo} · {source.path}",
            )

    def cleaned_refs(self) -> dict[str, str]:
        return {
            source.service_key: self.cleaned_data[f"ref_{source.service_key}"]
            for source in self._sources
        }


class ReconcileAdminMixin(admin.ModelAdmin[Feature]):
    """Adds the ``reconcile/`` and ``export/`` admin URLs and views to the Feature admin."""

    def get_urls(self) -> list[Any]:
        urls: list[Any] = super().get_urls()
        custom: list[Any] = [
            path(
                "reconcile/",
                self.admin_site.admin_view(self.reconcile_view),
                name="chains_feature_reconcile",
            ),
            path(
                "export/",
                self.admin_site.admin_view(self.export_view),
                name="chains_feature_export",
            ),
        ]
        return custom + urls

    def export_view(self, request: HttpRequest) -> HttpResponse:
        if not self.has_view_permission(request):
            raise PermissionDenied

        service_key = request.GET.get("service", "")
        payload: str | None = None
        error: str | None = None
        if service_key:
            try:
                document = build_declaration_document(service_key)
            except ServiceNotFound:
                error = f"No Service with key '{service_key}'."
            else:
                payload = json.dumps(document, indent=2)
                blank = blank_description_keys(document)
                if blank:
                    self.message_user(
                        request,
                        "These features have a blank description, which the declaration "
                        f"schema rejects. Add a description first: {', '.join(blank)}",
                        level=messages.WARNING,
                    )
                if request.GET.get("download") == "1":
                    response = HttpResponse(payload, content_type="application/json")
                    response["Content-Disposition"] = (
                        f'attachment; filename="remote-config.{service_key}.json"'
                    )
                    return response

        context = {
            **self.admin_site.each_context(request),
            "title": "Export declaration",
            "service_keys": _export_service_keys(),
            "selected": service_key,
            "payload": payload,
            "error": error,
        }
        return TemplateResponse(request, "admin/chains/export_flags.html", context)

    def reconcile_view(self, request: HttpRequest) -> HttpResponse:
        if not self.has_change_permission(request):
            raise PermissionDenied

        sources = get_sources()
        if request.method == "POST":
            return self._apply_reconcile(request, sources)

        drift = request.GET.get("drift") == "1"
        results: list[SourceResult] = []
        if drift:
            form = ReconcileForm(sources, drift=True)
            refs = {source.service_key: source.default_ref for source in sources}
            results = build_source_results(refs)
        elif "compute" in request.GET:
            form = ReconcileForm(sources, request.GET)
            if form.is_valid():
                results = build_source_results(form.cleaned_refs())
        else:
            form = ReconcileForm(sources)

        context = {
            **self.admin_site.each_context(request),
            "title": "Reconcile flags",
            "form": form,
            "results": results,
            "drift": drift,
            "computed": drift or ("compute" in request.GET),
        }
        return TemplateResponse(
            request, "admin/chains/reconcile_flags.html", context
        )

    def _apply_reconcile(
        self, request: HttpRequest, sources: list[RemoteConfigSource]
    ) -> HttpResponse:
        tokens = request.POST.getlist("apply")
        try:
            changes = [change_from_token(token) for token in tokens]
        except ValueError as error:
            self.message_user(
                request, f"Invalid selection: {error}", level=messages.ERROR
            )
            return redirect(request.path)

        actor = request.user
        if not isinstance(actor, get_user_model()):
            raise PermissionDenied
        missing = _missing_permissions(actor, changes)
        if missing:
            self.message_user(
                request,
                f"Nothing applied. The selection needs these permissions: "
                f"{', '.join(sorted(missing))}.",
                level=messages.ERROR,
            )
            return redirect(request.path)
        result = apply_changes(changes, actor=actor)
        self._remember_refs(request, sources, actor)
        message = (
            f"Applied {result.total} change(s): {result.added} add, "
            f"{result.attached} attach, {result.updated} update, "
            f"{result.detached} detach, {result.deleted} delete."
        )
        if result.skipped:
            message += (
                f" Skipped {result.skipped} change(s) because the database changed "
                f"after the diff; compute the diff again."
            )
        self.message_user(
            request, message, level=messages.WARNING if result.skipped else messages.SUCCESS
        )
        return redirect(request.path)

    def _remember_refs(
        self,
        request: HttpRequest,
        sources: list[RemoteConfigSource],
        actor: User,
    ) -> None:
        for source in sources:
            ref = request.POST.get(f"ref_{source.service_key}")
            if ref:
                RemoteConfigReconcileRef.objects.update_or_create(
                    service_key=source.service_key,
                    defaults={"ref": ref, "updated_by": actor},
                )
