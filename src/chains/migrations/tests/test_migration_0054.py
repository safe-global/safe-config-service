# SPDX-License-Identifier: FSL-1.1-MIT
from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations


class Migration0054TestCase(TestMigrations):
    migrate_from = "0053_remove_feature_enable_by_default"
    migrate_to = "0054_add_feature_enable_by_default"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        """Set up a feature before the migration adds enable_by_default back"""
        Feature = apps.get_model("chains", "Feature")
        Feature.objects.create(
            key="existing-feature",
            description="Feature created before 0054",
        )

    def test_enable_by_default_field_added(self) -> None:
        """Test that the enable_by_default field is added with correct properties"""
        Feature = self.apps_registry.get_model("chains", "Feature")
        field = Feature._meta.get_field("enable_by_default")
        self.assertEqual(field.default, False)
        self.assertIn("automatically enabled when creating a chain", field.help_text)

    def test_existing_feature_has_default_false(self) -> None:
        """Test that existing features get enable_by_default=False"""
        Feature = self.apps_registry.get_model("chains", "Feature")
        feature = Feature.objects.get(key="existing-feature")
        self.assertFalse(feature.enable_by_default)

    def test_can_create_feature_with_enable_by_default_true(self) -> None:
        """Test that new features can have enable_by_default=True"""
        Feature = self.apps_registry.get_model("chains", "Feature")
        feature = Feature.objects.create(
            key="new-feature-enabled",
            description="New feature enabled by default",
            enable_by_default=True,
        )
        self.assertTrue(feature.enable_by_default)

    def test_can_create_feature_with_enable_by_default_false(self) -> None:
        """Test that new features default to enable_by_default=False"""
        Feature = self.apps_registry.get_model("chains", "Feature")
        feature = Feature.objects.create(
            key="new-feature-disabled",
            description="New feature not enabled by default",
        )
        self.assertFalse(feature.enable_by_default)
