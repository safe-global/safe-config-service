from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations


class Migration0013TestCase(TestMigrations):
    migrate_from = "0012_rename_visible_safeapp_listed"
    migrate_to = "0013_assign_safeapp_icon_url"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        SafeApp = apps.get_model("safe_apps", "SafeApp")
        SafeApp.objects.create(
            app_id=1,
            chain_ids=[1],
            description="No icon_url",
        )

        SafeApp.objects.create(
            app_id=2,
            chain_ids=[1],
            icon_url=None,
            description="Null icon_url",
        )

        SafeApp.objects.create(
            app_id=3,
            chain_ids=[1],
            icon_url="",
            description="Empty icon_url",
        )

        SafeApp.objects.create(
            app_id=4,
            chain_ids=[1],
            icon_url="existing/icon_url.jpg",
            description="Existing icon_url",
        )

    def test_icon_url_is_set(self) -> None:
        SafeApp = self.apps_registry.get_model("safe_apps", "SafeApp")

        app_1 = SafeApp.objects.get(app_id=1)
        app_2 = SafeApp.objects.get(app_id=2)
        app_3 = SafeApp.objects.get(app_id=3)
        app_4 = SafeApp.objects.get(app_id=4)

        self.assertEqual(app_1.icon_url.url, "/media/safe_apps/icon_url.jpg")
        self.assertEqual(app_2.icon_url.url, "/media/safe_apps/icon_url.jpg")
        self.assertEqual(app_3.icon_url.url, "/media/safe_apps/icon_url.jpg")
        self.assertEqual(app_4.icon_url.url, "/media/existing/icon_url.jpg")
