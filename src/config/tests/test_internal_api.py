# SPDX-License-Identifier: FSL-1.1-MIT
from typing import Any

from django.core.cache import caches
from django.urls import reverse
from rest_framework.test import APITestCase

from chains.tests.factories import ChainFactory, GasTokenFactory, ServiceFactory
from safe_apps.tests.factories import SafeAppFactory


class InternalApiMirrorTests(APITestCase):
    def setUp(self) -> None:
        chain = ChainFactory.create(id=1, short_name="eth")
        GasTokenFactory.create(chains=(chain,))
        ServiceFactory.create(key="cgw")
        SafeAppFactory.create(chain_ids=[1])

    def tearDown(self) -> None:
        caches["safe-apps"].clear()

    def test_internal_routes_return_the_public_payload(self) -> None:
        routes: list[tuple[str, list[Any]]] = [
            ("v1:about:detail", []),
            ("v1:safe-apps:list", []),
            ("v1:chains:list", []),
            ("v1:chains:detail", [1]),
            ("v1:chains:detail_by_short_name", ["eth"]),
            ("v1:chains:gas-tokens-list", [1]),
            ("v2:chains:list", ["cgw"]),
            ("v2:chains:detail", ["cgw", 1]),
        ]

        for name, args in routes:
            with self.subTest(route=name):
                public_url = reverse(name, args=args)
                internal_url = reverse(f"internal:{name}", args=args)

                public_response = self.client.get(public_url, format="json")
                internal_response = self.client.get(internal_url, format="json")

                self.assertEqual(internal_url, f"/internal{public_url}")
                self.assertEqual(internal_response.status_code, 200)
                self.assertEqual(internal_response.json(), public_response.json())

    def test_internal_about_reports_the_api_version(self) -> None:
        response = self.client.get(reverse("internal:v1:about:detail"), format="json")

        self.assertEqual(response.json()["apiVersion"], "v1")


class InternalApiPaginationTests(APITestCase):
    def test_next_page_stays_on_the_internal_api(self) -> None:
        ChainFactory.create_batch(41)

        response = self.client.get(reverse("internal:v1:chains:list"), format="json")

        self.assertEqual(
            response.json()["next"],
            "http://testserver/internal/api/v1/chains/?limit=40&offset=40",
        )


class SchemaSeparationTests(APITestCase):
    def _paths(self, schema_name: str) -> list[str]:
        response = self.client.get(reverse(schema_name, args=(".json",)))
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        base_path = schema["basePath"].rstrip("/")
        return [f"{base_path}{path}" for path in schema["paths"]]

    def test_public_schema_has_no_internal_paths(self) -> None:
        paths = self._paths("schema-json")

        self.assertIn("/api/v1/chains/", paths)
        self.assertEqual([p for p in paths if p.startswith("/internal")], [])

    def test_internal_schema_has_only_internal_paths(self) -> None:
        paths = self._paths("internal-schema-json")

        self.assertIn("/internal/api/v1/chains/", paths)
        self.assertIn("/internal/api/v2/chains/{service_key}/", paths)
        self.assertEqual([p for p in paths if not p.startswith("/internal")], [])

    def test_internal_swagger_ui(self) -> None:
        response = self.client.get(reverse("internal-schema-swagger-ui"))

        self.assertEqual(response.status_code, 200)
