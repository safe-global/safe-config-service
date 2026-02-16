from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations


class Migration0051TestCase(TestMigrations):
    migrate_from = "0050_alter_chain_block_explorer_uri_address_template_and_more"
    migrate_to = "0051_service"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        # No setup needed as we're testing the creation of a new model
        pass

    def test_service_model_created(self) -> None:
        """Test that the Service model is created with correct fields"""
        Service = self.apps_registry.get_model("chains", "Service")

        # Test that we can create a Service instance
        service = Service.objects.create(
            key="cgw",
            name="Client Gateway",
            description="Safe Client Gateway service"
        )

        self.assertEqual(service.key, "cgw")
        self.assertEqual(service.name, "Client Gateway")
        self.assertEqual(service.description, "Safe Client Gateway service")
        self.assertIsNotNone(service.id)

    def test_service_key_unique_constraint(self) -> None:
        """Test that the key field has a unique constraint"""
        Service = self.apps_registry.get_model("chains", "Service")

        # Create first service
        Service.objects.create(
            key="test-service",
            name="Test Service",
            description="A test service"
        )

        # Try to create another service with the same key
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Service.objects.create(
                key="test-service",  # Same key should fail
                name="Another Test Service",
                description="Another test service"
            )

    def test_service_description_default_empty(self) -> None:
        """Test that description field defaults to empty string"""
        Service = self.apps_registry.get_model("chains", "Service")

        # Create service without description
        service = Service.objects.create(
            key="minimal-service",
            name="Minimal Service"
        )

        self.assertEqual(service.description, "")

    def test_service_field_constraints(self) -> None:
        """Test field constraints and properties"""
        Service = self.apps_registry.get_model("chains", "Service")

        # Test max_length constraints by creating a service with long values
        long_key = "a" * 255  # Max length for key
        long_name = "b" * 255  # Max length for name
        long_description = "c" * 255  # Max length for description

        service = Service.objects.create(
            key=long_key,
            name=long_name,
            description=long_description
        )

        self.assertEqual(service.key, long_key)
        self.assertEqual(service.name, long_name)
        self.assertEqual(service.description, long_description)

    def test_service_model_fields_exist(self) -> None:
        """Test that all expected fields exist on the Service model"""
        Service = self.apps_registry.get_model("chains", "Service")

        # Get model fields
        field_names = [field.name for field in Service._meta.get_fields()]

        expected_fields = ["id", "key", "name", "description"]
        for field_name in expected_fields:
            self.assertIn(field_name, field_names)

    def test_service_key_field_properties(self) -> None:
        """Test specific properties of the key field"""
        Service = self.apps_registry.get_model("chains", "Service")

        key_field = Service._meta.get_field("key")

        self.assertTrue(key_field.unique)
        self.assertEqual(key_field.max_length, 255)
        self.assertIn("unique key that identifies this service", key_field.help_text)

    def test_service_name_field_properties(self) -> None:
        """Test specific properties of the name field"""
        Service = self.apps_registry.get_model("chains", "Service")

        name_field = Service._meta.get_field("name")

        self.assertEqual(name_field.max_length, 255)
        self.assertFalse(name_field.blank)

    def test_service_description_field_properties(self) -> None:
        """Test specific properties of the description field"""
        Service = self.apps_registry.get_model("chains", "Service")

        description_field = Service._meta.get_field("description")

        self.assertEqual(description_field.max_length, 255)
        self.assertTrue(description_field.blank)
        self.assertEqual(description_field.default, "")
