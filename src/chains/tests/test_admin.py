# SPDX-License-Identifier: FSL-1.1-MIT
from unittest.mock import patch

from django.contrib.admin import site
from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from ..admin import ChainAdmin, FeatureInline
from ..models import Chain, Feature
from .factories import ChainFactory, FeatureFactory


class ChainAdminGlobalFeaturesContextTests(TestCase):
    """Tests for ChainAdmin change_view and add_view global_features context."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = User.objects.create_superuser(
            "admin", "admin@example.com", "password"
        )

    def setUp(self) -> None:
        self.client = Client()
        self.client.force_login(self.superuser)

    def test_change_view_includes_global_features_in_context(self) -> None:
        """change_view passes global_features in extra_context with scope=GLOBAL."""
        chain = ChainFactory.create()
        global_feature = FeatureFactory.create(
            key="GLOBAL_FEATURE", scope=Feature.Scope.GLOBAL
        )
        url = reverse("admin:chains_chain_change", args=[chain.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"GLOBAL FEATURES ENABLED FOR THIS CHAIN", response.content)
        self.assertIn(global_feature.key.encode(), response.content)

    def test_add_view_includes_global_features_in_context(self) -> None:
        """add_view passes global_features in extra_context with scope=GLOBAL."""
        FeatureFactory.create(key="GLOBAL_ADD", scope=Feature.Scope.GLOBAL)
        url = reverse("admin:chains_chain_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"GLOBAL FEATURES ENABLED FOR THIS CHAIN", response.content)
        self.assertIn(b"GLOBAL_ADD", response.content)

    def test_global_features_queryset_filters_scope_and_orders_by_key(self) -> None:
        """global_features contains only GLOBAL scope and is ordered by key."""
        chain = ChainFactory.create()
        FeatureFactory.create(key="z_global", scope=Feature.Scope.GLOBAL)
        FeatureFactory.create(key="a_global", scope=Feature.Scope.GLOBAL)
        FeatureFactory.create(
            key="only_per_chain_list", scope=Feature.Scope.PER_CHAIN
        )
        url = reverse("admin:chains_chain_change", args=[chain.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        global_features = response.context["global_features"]
        keys = [f.key for f in global_features]
        self.assertEqual(keys, ["a_global", "z_global"])
        self.assertNotIn(
            "only_per_chain_list",
            keys,
            msg="PER_CHAIN feature must not appear in the global features list",
        )

    def test_change_view_hides_global_section_when_no_global_features(self) -> None:
        """Change view does not render global section when global_features is empty."""
        chain = ChainFactory.create()
        FeatureFactory.create(key="per_chain_feature", scope=Feature.Scope.PER_CHAIN)
        url = reverse("admin:chains_chain_change", args=[chain.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"GLOBAL FEATURES ENABLED FOR THIS CHAIN", response.content)

    def test_add_view_hides_global_section_when_no_global_features(self) -> None:
        """Add view does not render global section when global_features is empty."""
        url = reverse("admin:chains_chain_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"GLOBAL FEATURES ENABLED FOR THIS CHAIN", response.content)

    def test_global_feature_description_rendered_when_present(self) -> None:
        """Feature description is rendered when set."""
        chain = ChainFactory.create()
        FeatureFactory.create(
            key="WITH_DESC",
            description="My feature description",
            scope=Feature.Scope.GLOBAL,
        )
        url = reverse("admin:chains_chain_change", args=[chain.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"WITH_DESC", response.content)
        self.assertIn(b"My feature description", response.content)

    def test_global_feature_no_description_when_empty(self) -> None:
        """Feature list item does not show description suffix when description is empty."""
        chain = ChainFactory.create()
        FeatureFactory.create(
            key="NO_DESC",
            description="",
            scope=Feature.Scope.GLOBAL,
        )
        url = reverse("admin:chains_chain_change", args=[chain.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NO_DESC", response.content)
        # Template only outputs " - description" when f.description is truthy
        self.assertNotIn(
            b"NO_DESC - ",
            response.content,
            msg="Empty description should not render ' - ' after key",
        )

    def test_global_feature_link_has_correct_change_url(self) -> None:
        """Rendered HTML includes correct admin change URL for each global feature."""
        chain = ChainFactory.create()
        global_feature = FeatureFactory.create(
            key="LINKED_FEATURE",
            scope=Feature.Scope.GLOBAL,
        )
        expected_url = reverse(
            "admin:chains_feature_change", args=[global_feature.pk]
        )
        url = reverse("admin:chains_chain_change", args=[chain.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            expected_url.encode(),
            response.content,
            msg="Feature change URL should appear in rendered HTML",
        )
        self.assertIn(b"LINKED_FEATURE", response.content)

    def test_change_view_sets_global_features_queryset_scope_and_order(self) -> None:
        """change_view passes extra_context with global_features (GLOBAL scope, ordered by key)."""
        from django.contrib.admin import ModelAdmin
        from django.test import RequestFactory

        chain = ChainFactory.create()
        FeatureFactory.create(key="b", scope=Feature.Scope.GLOBAL)
        FeatureFactory.create(key="a", scope=Feature.Scope.GLOBAL)
        request = RequestFactory().get("/")
        request.user = User.objects.create_superuser(
            "u", "u@example.com", "pass"
        )
        model_admin = ChainAdmin(Chain, site)
        captured: list = []
        real_change_view = ModelAdmin.change_view

        def capturing_change_view(
            self, request, object_id, form_url="", extra_context=None
        ):  # noqa: N802
            captured.append(extra_context)
            return real_change_view(
                self, request, object_id, form_url, extra_context
            )

        with patch.object(ModelAdmin, "change_view", capturing_change_view):
            model_admin.change_view(
                request, str(chain.pk), extra_context={"existing": True}
            )
        self.assertEqual(len(captured), 1)
        passed = captured[0]
        self.assertIsNotNone(passed)
        self.assertIn("global_features", passed)
        self.assertIn("existing", passed)
        keys = [f.key for f in passed["global_features"]]
        self.assertEqual(keys, ["a", "b"])
        self.assertTrue(
            all(f.scope == Feature.Scope.GLOBAL for f in passed["global_features"])
        )

    def test_add_view_sets_global_features_queryset_scope_and_order(self) -> None:
        """add_view passes extra_context with global_features (GLOBAL scope, ordered by key)."""
        from django.contrib.admin import ModelAdmin
        from django.test import RequestFactory

        FeatureFactory.create(key="m", scope=Feature.Scope.GLOBAL)
        FeatureFactory.create(key="k", scope=Feature.Scope.GLOBAL)
        request = RequestFactory().get("/")
        request.user = User.objects.create_superuser(
            "u2", "u2@example.com", "pass"
        )
        model_admin = ChainAdmin(Chain, site)
        captured: list = []
        real_add_view = ModelAdmin.add_view

        def capturing_add_view(
            self, request, form_url="", extra_context=None
        ):  # noqa: N802
            captured.append(extra_context)
            return real_add_view(self, request, form_url, extra_context)

        with patch.object(ModelAdmin, "add_view", capturing_add_view):
            model_admin.add_view(request, extra_context={"existing": True})
        self.assertEqual(len(captured), 1)
        passed = captured[0]
        self.assertIsNotNone(passed)
        self.assertIn("global_features", passed)
        self.assertIn("existing", passed)
        keys = [f.key for f in passed["global_features"]]
        self.assertEqual(keys, ["k", "m"])
        self.assertTrue(
            all(f.scope == Feature.Scope.GLOBAL for f in passed["global_features"])
        )


class FeatureInlineQuerysetTests(TestCase):
    """FeatureInline.get_queryset() must exclude GLOBAL feature associations."""

    def setUp(self) -> None:
        self.request = RequestFactory().get("/")
        self.request.user = User.objects.create_superuser(
            "admin", "admin@example.com", "password"
        )
        self.inline = FeatureInline(Chain, site)

    def test_global_feature_association_excluded(self) -> None:
        chain = ChainFactory.create()
        global_feature = FeatureFactory.create(scope=Feature.Scope.GLOBAL)
        global_feature.chains.add(chain)

        qs = self.inline.get_queryset(self.request)

        self.assertFalse(
            qs.filter(feature=global_feature, chain=chain).exists(),
            "GLOBAL feature association must not appear in the inline queryset",
        )

    def test_per_chain_feature_association_included(self) -> None:
        chain = ChainFactory.create()
        per_chain_feature = FeatureFactory.create(scope=Feature.Scope.PER_CHAIN)
        per_chain_feature.chains.add(chain)

        qs = self.inline.get_queryset(self.request)

        self.assertTrue(
            qs.filter(feature=per_chain_feature, chain=chain).exists(),
            "PER_CHAIN feature association must appear in the inline queryset",
        )

    def test_mixed_features_only_per_chain_included(self) -> None:
        chain = ChainFactory.create()
        global_feature = FeatureFactory.create(scope=Feature.Scope.GLOBAL)
        per_chain_feature = FeatureFactory.create(scope=Feature.Scope.PER_CHAIN)
        global_feature.chains.add(chain)
        per_chain_feature.chains.add(chain)

        qs = self.inline.get_queryset(self.request).filter(chain=chain)

        feature_ids = set(qs.values_list("feature_id", flat=True))
        self.assertIn(per_chain_feature.pk, feature_ids)
        self.assertNotIn(global_feature.pk, feature_ids)
