# SPDX-License-Identifier: FSL-1.1-MIT
"""Admin "Reconcile flags" view: diff declarations at a ref vs the DB and apply.

Mixed into ``FeatureAdmin`` via :class:`ReconcileAdminMixin`. Standard Django
admin extension (``get_urls`` + ``TemplateResponse``), following the existing
``change_form.html`` customization style.
"""
from dataclasses import dataclass, replace
from typing import Any

from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from .models import RemoteConfigReconcileRef, Service
from .remote_config.apply import apply_changes
from .remote_config.declaration import DeclarationError, parse_declaration_text
from .remote_config.diff import Change, ChangeType, diff_service
from .remote_config.github import DeclarationFetchError, fetch_declaration_text
from .remote_config.sources import RemoteConfigSource, get_sources
from .remote_config.state import known_chain_ids, load_feature_states
from .remote_config.tokens import change_from_token, change_to_token


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


def _delta_units(change: Change) -> list[ApplyUnit]:
    """Split a change's field deltas into authoritative vs informational units.

    Authoritative (description/scope) deltas are grouped and pre-checked;
    the chains delta is a separate, un-checked unit (decision #6).
    """
    units: list[ApplyUnit] = []
    authoritative = tuple(d for d in change.deltas if d.authoritative)
    informational = tuple(d for d in change.deltas if not d.authoritative)

    if authoritative:
        unit_change = Change(
            type=ChangeType.UPDATE,
            service_key=change.service_key,
            key=change.key,
            feature_id=change.feature_id,
            deltas=authoritative,
        )
        detail = "; ".join(
            f"{d.name}: {d.current!r} → {d.declared!r}" for d in authoritative
        )
        units.append(
            ApplyUnit(change_to_token(unit_change), f"UPDATE {change.key}", detail, True, ())
        )

    if informational:
        unit_change = Change(
            type=ChangeType.UPDATE,
            service_key=change.service_key,
            key=change.key,
            feature_id=change.feature_id,
            deltas=informational,
        )
        delta = informational[0]
        detail = f"chains: {delta.current} → {delta.declared} (release default — review)"
        units.append(
            ApplyUnit(
                change_to_token(unit_change), f"UPDATE {change.key} chains", detail, False, ()
            )
        )
    return units


def units_for_change(change: Change) -> list[ApplyUnit]:
    """Expand a :class:`Change` into one or more checkbox units."""
    if change.type is ChangeType.ADD:
        detail = f"scope={change.declared_scope}"
        if change.declared_chains:
            detail += f", chains={', '.join(change.declared_chains)}"
        return [
            ApplyUnit(change_to_token(change), f"ADD {change.key}", detail, True, change.warnings)
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
        units.extend(_delta_units(change))
        return units

    if change.type is ChangeType.UPDATE:
        return _delta_units(change)

    if change.type is ChangeType.DETACH:
        return [
            ApplyUnit(
                change_to_token(change),
                f"DETACH {change.key} from {change.service_key}",
                f"remaining services: {change.remaining_services_after}",
                False,
                (),
            )
        ]

    return [
        ApplyUnit(
            change_to_token(change),
            f"DELETE {change.key}",
            "no remaining services",
            False,
            (),
        )
    ]


def build_source_results(
    refs: dict[str, str], read_only: bool = False
) -> list[SourceResult]:
    """Fetch + diff every configured source at its ref. Errors are per-source."""
    states = load_feature_states()
    chain_ids = known_chain_ids()
    existing_services = set(Service.objects.values_list("key", flat=True))
    results: list[SourceResult] = []

    for source in get_sources():
        ref = refs.get(source.service_key) or source.default_ref
        warnings: list[str] = []
        try:
            text = fetch_declaration_text(source.repo, ref, source.path)
            declaration = parse_declaration_text(text)
        except (DeclarationFetchError, DeclarationError) as error:
            results.append(
                SourceResult(
                    source, ref, [], str(error), source.service_key in existing_services, []
                )
            )
            continue

        if declaration.service != source.service_key:
            warnings.append(
                f"Declared service '{declaration.service}' does not match configured "
                f"'{source.service_key}'; diffing against '{source.service_key}'."
            )

        changes = diff_service(
            source.service_key, declaration.features, states, chain_ids
        )
        units = [unit for change in changes for unit in units_for_change(change)]
        results.append(
            SourceResult(
                source, ref, units, None, source.service_key in existing_services, warnings
            )
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


class ReconcileAdminMixin:
    """Adds the ``reconcile/`` admin URL and view to a ModelAdmin."""

    def get_urls(self) -> list[Any]:
        urls: list[Any] = super().get_urls()  # type: ignore[misc]
        custom: list[Any] = [
            path(
                "reconcile/",
                self.admin_site.admin_view(self.reconcile_view),  # type: ignore[attr-defined]
                name="chains_feature_reconcile",
            )
        ]
        return custom + urls

    def reconcile_view(self, request: HttpRequest) -> HttpResponse:
        if not self.has_change_permission(request):  # type: ignore[attr-defined]
            raise PermissionDenied

        sources = get_sources()
        if request.method == "POST":
            return self._apply_reconcile(request, sources)

        drift = request.GET.get("drift") == "1"
        results: list[SourceResult] = []
        if drift:
            form = ReconcileForm(sources, drift=True)
            refs = {source.service_key: source.default_ref for source in sources}
            results = build_source_results(refs, read_only=True)
        elif "compute" in request.GET:
            form = ReconcileForm(sources, request.GET)
            if form.is_valid():
                results = build_source_results(form.cleaned_refs())
        else:
            form = ReconcileForm(sources)

        context = {
            **self.admin_site.each_context(request),  # type: ignore[attr-defined]
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
            self.message_user(  # type: ignore[attr-defined]
                request, f"Invalid selection: {error}", level=messages.ERROR
            )
            return redirect(request.path)

        result = apply_changes(changes, actor=request.user)
        self._remember_refs(request, sources)
        self.message_user(  # type: ignore[attr-defined]
            request,
            f"Applied {result.total} change(s): {result.added} add, "
            f"{result.attached} attach, {result.updated} update, "
            f"{result.detached} detach, {result.deleted} delete.",
        )
        return redirect(request.path)

    def _remember_refs(
        self, request: HttpRequest, sources: list[RemoteConfigSource]
    ) -> None:
        for source in sources:
            ref = request.POST.get(f"ref_{source.service_key}")
            if ref:
                RemoteConfigReconcileRef.objects.update_or_create(
                    service_key=source.service_key,
                    # reconcile_view requires an authenticated staff user, so
                    # request.user is never AnonymousUser here.
                    defaults={"ref": ref, "updated_by": request.user},  # type: ignore[misc]
                )
