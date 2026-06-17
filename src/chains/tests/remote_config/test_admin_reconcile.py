# SPDX-License-Identifier: FSL-1.1-MIT
import responses
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from chains.models import Feature, RemoteConfigReconcileRef
from chains.remote_config.diff import Change, ChangeType
from chains.remote_config.tokens import change_to_token

BASE = "https://raw.example.test"
WEB_URL = f"{BASE}/safe-global/safe-wallet-monorepo/main/apps/web/config/remote-config.json"
SOURCES = [
    {
        "label": "Web",
        "service_key": "WALLET_WEB",
        "repo": "safe-global/safe-wallet-monorepo",
        "path": "apps/web/config/remote-config.json",
        "default_ref": "main",
    }
]


@override_settings(
    REMOTE_CONFIG_RAW_BASE_URL=BASE,
    REMOTE_CONFIG_SOURCES=SOURCES,
    REMOTE_CONFIG_GITHUB_TOKEN=None,
)
class ReconcileAdminViewTestCase(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_superuser(
            username="op", email="op@example.test", password="pw"
        )
        self.client.force_login(self.user)
        self.url = reverse("admin:chains_feature_reconcile")

    def test_requires_login(self) -> None:
        self.client.logout()
        response = self.client.get(self.url)
        assert response.status_code in (302, 403)

    def test_get_renders_ref_form(self) -> None:
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, "Reconcile flags")
        self.assertContains(response, "ref_WALLET_WEB")

    @responses.activate
    def test_compute_lists_add_for_declared_missing_flag(self) -> None:
        responses.add(
            responses.GET,
            WEB_URL,
            status=200,
            body='{"service":"WALLET_WEB","features":'
            '[{"key":"NEWFLAG","description":"x","scope":"GLOBAL"}]}',
        )

        response = self.client.get(
            self.url, {"compute": "1", "ref_WALLET_WEB": "main"}
        )

        assert response.status_code == 200
        self.assertContains(response, "ADD NEWFLAG")

    @responses.activate
    def test_compute_surfaces_fetch_error_per_source(self) -> None:
        responses.add(responses.GET, WEB_URL, status=404)

        response = self.client.get(
            self.url, {"compute": "1", "ref_WALLET_WEB": "main"}
        )

        assert response.status_code == 200
        self.assertContains(response, "not found")

    def test_apply_creates_feature_and_remembers_ref(self) -> None:
        token = change_to_token(
            Change(
                type=ChangeType.ADD,
                service_key="WALLET_WEB",
                key="NEWFLAG",
                declared_description="x",
                declared_scope="GLOBAL",
            )
        )

        response = self.client.post(
            self.url, {"apply": [token], "ref_WALLET_WEB": "feat/my-branch"}
        )

        assert response.status_code == 302
        assert Feature.objects.filter(key="NEWFLAG").exists()
        remembered = RemoteConfigReconcileRef.objects.get(service_key="WALLET_WEB")
        assert remembered.ref == "feat/my-branch"
        assert remembered.updated_by == self.user

    def test_apply_rejects_malformed_token(self) -> None:
        before = Feature.objects.count()

        response = self.client.post(
            self.url, {"apply": ["not-a-valid-token"], "ref_WALLET_WEB": "main"}
        )

        assert response.status_code == 302
        # Nothing was applied (the DB has migration-seeded features, so assert no
        # net change rather than an empty table).
        assert Feature.objects.count() == before

    @responses.activate
    def test_drift_view_is_read_only(self) -> None:
        responses.add(responses.GET, WEB_URL, status=404)

        response = self.client.get(self.url, {"drift": "1"})

        assert response.status_code == 200
        self.assertNotContains(response, "Apply selected changes")
