# SPDX-License-Identifier: FSL-1.1-MIT
"""Cross-source conflict handling for Feature-level fields (description/scope)."""
import responses
from django.test import TestCase, override_settings

from chains.admin_views import (
    _cross_source_conflicts,
    build_source_results,
    units_for_change,
)
from chains.models import Feature
from chains.remote_config.declaration import parse_declaration
from chains.remote_config.diff import Change, ChangeType, FieldDelta

from ..factories import FeatureFactory, ServiceFactory

BASE = "https://raw.example.test"
WEB_URL = f"{BASE}/r/main/web.json"
CGW_URL = f"{BASE}/r/main/cgw.json"
TWO_SOURCES = [
    {
        "label": "Web",
        "service_key": "WALLET_WEB",
        "repo": "r",
        "path": "web.json",
        "default_ref": "main",
    },
    {
        "label": "CGW",
        "service_key": "CGW",
        "repo": "r",
        "path": "cgw.json",
        "default_ref": "main",
    },
]


def _decl(service: str, description: str, scope: str = "PER_CHAIN") -> object:
    return parse_declaration(
        {
            "service": service,
            "features": [{"key": "SHARED", "description": description, "scope": scope}],
        }
    )


class CrossSourceConflictTestCase(TestCase):
    def test_detects_differing_description(self) -> None:
        conflicts = _cross_source_conflicts(
            {"WALLET_WEB": _decl("WALLET_WEB", "A"), "CGW": _decl("CGW", "B")}
        )
        assert conflicts == {"SHARED": frozenset({"description"})}

    def test_detects_differing_scope(self) -> None:
        conflicts = _cross_source_conflicts(
            {
                "WALLET_WEB": _decl("WALLET_WEB", "A", "PER_CHAIN"),
                "CGW": _decl("CGW", "A", "GLOBAL"),
            }
        )
        assert conflicts == {"SHARED": frozenset({"scope"})}

    def test_no_conflict_when_fields_match(self) -> None:
        conflicts = _cross_source_conflicts(
            {"WALLET_WEB": _decl("WALLET_WEB", "A"), "CGW": _decl("CGW", "A")}
        )
        assert conflicts == {}


class ConflictAwareUnitsTestCase(TestCase):
    def _update(self) -> Change:
        return Change(
            type=ChangeType.UPDATE,
            service_key="WALLET_WEB",
            key="SHARED",
            feature_id=1,
            deltas=(FieldDelta("description", "old", "new", True),),
        )

    def test_conflicting_update_is_unchecked_and_warned(self) -> None:
        units = units_for_change(self._update(), frozenset({"description"}))
        assert len(units) == 1
        assert units[0].default_checked is False
        assert units[0].warnings
        assert "different description" in units[0].warnings[0]

    def test_nonconflicting_update_is_prechecked(self) -> None:
        units = units_for_change(self._update(), frozenset())
        assert units[0].default_checked is True
        assert units[0].warnings == ()


@override_settings(REMOTE_CONFIG_RAW_BASE_URL=BASE, REMOTE_CONFIG_SOURCES=TWO_SOURCES)
class BuildSourceResultsConflictTestCase(TestCase):
    @responses.activate
    def test_shared_key_with_differing_descriptions_warns_and_unchecks(self) -> None:
        web = ServiceFactory(key="WALLET_WEB")
        cgw = ServiceFactory(key="CGW")
        FeatureFactory(
            key="SHARED",
            description="db value",
            scope=Feature.Scope.PER_CHAIN,
            services=[web, cgw],
        )
        responses.add(
            responses.GET,
            WEB_URL,
            body='{"service":"WALLET_WEB","features":'
            '[{"key":"SHARED","description":"web text","scope":"PER_CHAIN"}]}',
        )
        responses.add(
            responses.GET,
            CGW_URL,
            body='{"service":"CGW","features":'
            '[{"key":"SHARED","description":"cgw text","scope":"PER_CHAIN"}]}',
        )

        results = build_source_results({"WALLET_WEB": "main", "CGW": "main"})

        web_result = next(r for r in results if r.source.service_key == "WALLET_WEB")
        assert any("different description" in w for w in web_result.warnings)
        # The conflicting description update must not be pre-checked.
        assert web_result.units
        assert all(not unit.default_checked for unit in web_result.units)
