# SPDX-License-Identifier: FSL-1.1-MIT
from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations


class Migration0053TestCase(TestMigrations):
    migrate_from = "0052_feature_scope_services"
    migrate_to = "0053_remove_feature_enable_by_default"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        Feature = apps.get_model("chains", "Feature")
        Feature.objects.create(
            key="test-feature",
            description="Test feature",
            enable_by_default=True,
            scope="PER_CHAIN",
        )

    def test_feature_preserved(self) -> None:
        Feature = self.apps_registry.get_model("chains", "Feature")
        feature = Feature.objects.get(key="test-feature")
        self.assertEqual(feature.description, "Test feature")

    def test_enable_by_default_removed(self) -> None:
        Feature = self.apps_registry.get_model("chains", "Feature")
        field_names = [f.name for f in Feature._meta.get_fields()]
        self.assertNotIn("enable_by_default", field_names)
