# SPDX-License-Identifier: FSL-1.1-MIT
import json
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from chains.models import Feature

from ..factories import ChainFactory, FeatureFactory, ServiceFactory


class ExportRemoteConfigTestCase(TestCase):
    def test_exports_features_ordered_by_key(self) -> None:
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

        out = StringIO()
        call_command("export_remote_config", service="WALLET_WEB", stdout=out)
        document = json.loads(out.getvalue())

        assert document["service"] == "WALLET_WEB"
        assert document["$schema"] == "./remote-config.schema.json"
        assert [f["key"] for f in document["features"]] == ["CSV_TX_EXPORT", "SPACES"]

        spaces = next(f for f in document["features"] if f["key"] == "SPACES")
        assert spaces["scope"] == "PER_CHAIN"
        assert spaces["defaultChains"] == [str(chain.id)]

        csv = next(f for f in document["features"] if f["key"] == "CSV_TX_EXPORT")
        assert csv["defaultChains"] == []

    def test_errors_on_unknown_service(self) -> None:
        with self.assertRaises(CommandError):
            call_command("export_remote_config", service="DOES_NOT_EXIST")
