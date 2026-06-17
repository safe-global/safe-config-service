# SPDX-License-Identifier: FSL-1.1-MIT
import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from chains.models import Feature
from chains.remote_config.export import ServiceNotFound, build_declaration_document

from ..factories import ChainFactory, FeatureFactory, ServiceFactory

SOURCES = [
    {
        "label": "Web",
        "service_key": "WALLET_WEB",
        "repo": "safe-global/safe-wallet-monorepo",
        "path": "apps/web/config/remote-config.json",
        "default_ref": "dev",
    }
]


class BuildDeclarationDocumentTestCase(TestCase):
    def test_builds_sorted_document(self) -> None:
        chain = ChainFactory()
        service = ServiceFactory(key="WALLET_WEB")
        FeatureFactory(
            key="SPACES",
            description="Spaces.",
            scope=Feature.Scope.PER_CHAIN,
            chains=[chain],
            services=[service],
        )
        FeatureFactory(
            key="CSV_TX_EXPORT",
            description="CSV.",
            scope=Feature.Scope.GLOBAL,
            services=[service],
        )

        document = build_declaration_document("WALLET_WEB")

        assert document["service"] == "WALLET_WEB"
        assert document["$schema"] == "./remote-config.schema.json"
        assert [f["key"] for f in document["features"]] == ["CSV_TX_EXPORT", "SPACES"]
        spaces = next(f for f in document["features"] if f["key"] == "SPACES")
        assert spaces["defaultChains"] == [str(chain.id)]

    def test_raises_for_unknown_service(self) -> None:
        with self.assertRaises(ServiceNotFound):
            build_declaration_document("NOPE")


@override_settings(REMOTE_CONFIG_SOURCES=SOURCES)
class ExportViewTestCase(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_superuser(
            username="op", email="op@example.test", password="pw"
        )
        self.client.force_login(self.user)
        self.url = reverse("admin:chains_feature_export")

    def test_requires_login(self) -> None:
        self.client.logout()
        assert self.client.get(self.url).status_code in (302, 403)

    def test_get_lists_configured_service_in_picker(self) -> None:
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, "Export declaration")
        self.assertContains(response, "WALLET_WEB")

    def test_shows_declaration_for_selected_service(self) -> None:
        service = ServiceFactory(key="WALLET_WEB")
        FeatureFactory(key="SPACES", scope=Feature.Scope.GLOBAL, services=[service])

        response = self.client.get(self.url, {"service": "WALLET_WEB"})

        assert response.status_code == 200
        self.assertContains(response, "SPACES")

    def test_download_returns_json_attachment(self) -> None:
        service = ServiceFactory(key="WALLET_WEB")
        FeatureFactory(key="SPACES", scope=Feature.Scope.GLOBAL, services=[service])

        response = self.client.get(
            self.url, {"service": "WALLET_WEB", "download": "1"}
        )

        assert response["Content-Type"] == "application/json"
        assert "attachment" in response["Content-Disposition"]
        assert "remote-config.WALLET_WEB.json" in response["Content-Disposition"]
        document = json.loads(response.content)
        assert document["service"] == "WALLET_WEB"

    def test_unknown_service_shows_error(self) -> None:
        response = self.client.get(self.url, {"service": "GHOST"})
        assert response.status_code == 200
        self.assertContains(response, "No Service with key")
