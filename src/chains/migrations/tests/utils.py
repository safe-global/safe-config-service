from django.apps import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import StateApps
from django.test import TestCase


# Use this TestCase class in order to test migrations
# migrate_from – the name of the migration where the test starts
# migrate_to – the target migration
#
# Example:
# You can set models on a specific migration inside your implementation of setUpBeforeMigration()
# The validation can then be performed on each test function of the Test class
# This class is heavily inspired by https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
class TestMigrations(TestCase):
    @property
    def app(self) -> str:
        app_config = apps.get_containing_app_config(type(self).__module__)
        if app_config is None:
            raise Exception("Could not retrieve app configuration")  # pragma: no cover
        return app_config.name

    migrate_from: str
    migrate_to: str
    apps_registry: StateApps

    def setUp(self) -> None:
        assert (
            self.migrate_from and self.migrate_to
        ), "TestCase '{}' must define migrate_from and migrate_to     properties".format(
            type(self).__name__
        )
        migrate_from: tuple[str, str] = (self.app, self.migrate_from)
        migrate_to: tuple[str, str] = (self.app, self.migrate_to)
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(migrate_from).apps

        # Reverse to the original migration
        executor.migrate([migrate_from])

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate([migrate_to])

        self.apps_registry = executor.loader.project_state(migrate_to).apps

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        pass  # pragma: no cover
