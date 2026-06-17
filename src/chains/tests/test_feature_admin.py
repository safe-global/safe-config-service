# SPDX-License-Identifier: FSL-1.1-MIT
from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from ..admin import FeatureAdmin
from ..models import Feature
from .factories import ChainFactory, FeatureFactory, ServiceFactory


class FeatureAdminDisplayTestCase(TestCase):
    def setUp(self) -> None:
        self.admin = FeatureAdmin(Feature, AdminSite())

    def test_services_display_is_sorted(self) -> None:
        feature = FeatureFactory(
            services=[ServiceFactory(key="WALLET_WEB"), ServiceFactory(key="CGW")]
        )
        assert self.admin.services_display(feature) == "CGW, WALLET_WEB"

    def test_services_display_when_none(self) -> None:
        assert "—" in self.admin.services_display(FeatureFactory())

    def test_chains_display_global(self) -> None:
        feature = FeatureFactory(scope=Feature.Scope.GLOBAL)
        assert "all chains" in self.admin.chains_display(feature)

    def test_chains_display_per_chain_sorted_numerically(self) -> None:
        feature = FeatureFactory(
            scope=Feature.Scope.PER_CHAIN,
            chains=[ChainFactory(id=10), ChainFactory(id=2)],
        )
        # Numeric sort (2, 10), not lexicographic ("10", "2").
        assert "2, 10" in self.admin.chains_display(feature)

    def test_chains_display_per_chain_empty(self) -> None:
        feature = FeatureFactory(scope=Feature.Scope.PER_CHAIN)
        assert "none" in self.admin.chains_display(feature)
