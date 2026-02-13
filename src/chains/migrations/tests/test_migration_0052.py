from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations


class Migration0052TestCase(TestMigrations):
    migrate_from = "0051_service"
    migrate_to = "0052_feature_scope_services"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        """Set up test data before the migration"""
        Chain = apps.get_model("chains", "Chain")
        Feature = apps.get_model("chains", "Feature")
        Service = apps.get_model("chains", "Service")

        # Create test chains
        self.chain1 = Chain.objects.create(
            id=1,
            name="Ethereum",
            short_name="eth",
            description="Ethereum Mainnet",
            l2=False,
            rpc_authentication="API_KEY_PATH",
            rpc_uri="https://mainnet.infura.io/v3/",
            safe_apps_rpc_authentication="API_KEY_PATH",
            safe_apps_rpc_uri="https://mainnet.infura.io/v3/",
            block_explorer_uri_address_template="https://etherscan.io/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://etherscan.io/tx/{{txHash}}",
            currency_name="Ether",
            currency_symbol="ETH",
            currency_decimals=18,
            currency_logo_uri="https://example.com/eth-logo.png",
            transaction_service_uri="https://safe-transaction-mainnet.safe.global",
            vpc_transaction_service_uri="",
            theme_text_color="#001428",
            theme_background_color="#E8E7E6",
            ens_registry_address="0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e",
            recommended_master_copy_version="1.3.0",
            prices_provider_native_coin="ethereum",
            prices_provider_chain_name="ethereum",
            hidden=False,
            balances_provider_chain_name="ethereum",
            balances_provider_enabled=True,
        )

        self.chain2 = Chain.objects.create(
            id=137,
            name="Polygon",
            short_name="matic",
            description="Polygon Mainnet",
            l2=True,
            rpc_authentication="API_KEY_PATH",
            rpc_uri="https://polygon-mainnet.infura.io/v3/",
            safe_apps_rpc_authentication="API_KEY_PATH",
            safe_apps_rpc_uri="https://polygon-mainnet.infura.io/v3/",
            block_explorer_uri_address_template="https://polygonscan.com/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://polygonscan.com/tx/{{txHash}}",
            currency_name="MATIC",
            currency_symbol="MATIC",
            currency_decimals=18,
            currency_logo_uri="https://example.com/matic-logo.png",
            transaction_service_uri="https://safe-transaction-polygon.safe.global",
            vpc_transaction_service_uri="",
            theme_text_color="#8B5CF6",
            theme_background_color="#F3F4F6",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
            prices_provider_native_coin="matic-network",
            prices_provider_chain_name="polygon-pos",
            hidden=False,
            balances_provider_chain_name="polygon",
            balances_provider_enabled=True,
        )

        # Create test services
        self.service1 = Service.objects.create(
            key="cgw",
            name="Client Gateway",
            description="Safe Client Gateway service"
        )

        self.service2 = Service.objects.create(
            key="frontend",
            name="Safe Frontend",
            description="Safe web interface"
        )

        # Create test features (before migration - no scope or services fields)
        self.feature1 = Feature.objects.create(
            key="test-feature-1",
            description="Test feature 1"
        )

        self.feature2 = Feature.objects.create(
            key="test-feature-2",
            description="Test feature 2"
        )

        # Add chains to features using the M2M relationship
        self.feature1.chains.add(self.chain1)
        self.feature2.chains.add(self.chain1, self.chain2)

    def test_scope_field_added(self) -> None:
        """Test that the scope field is added with correct properties"""
        Feature = self.apps_registry.get_model("chains", "Feature")

        # Get the scope field
        scope_field = Feature._meta.get_field("scope")

        # Test field properties
        self.assertEqual(scope_field.max_length, 10)
        self.assertEqual(scope_field.default, "PER_CHAIN")
        self.assertIn("Global applies to all chains", scope_field.help_text)

        # Test choices
        expected_choices = [("GLOBAL", "Global"), ("PER_CHAIN", "Per-chain")]
        self.assertEqual(scope_field.choices, expected_choices)

    def test_services_field_added(self) -> None:
        """Test that the services M2M field is added with correct properties"""
        Feature = self.apps_registry.get_model("chains", "Feature")

        # Get the services field
        services_field = Feature._meta.get_field("services")

        # Test field properties
        self.assertTrue(services_field.many_to_many)
        self.assertTrue(services_field.blank)
        self.assertEqual(services_field.related_model._meta.label, "chains.Service")
        self.assertIn("Services that have access to this feature", services_field.help_text)

    def test_chains_field_altered(self) -> None:
        """Test that the chains field help text is updated"""
        Feature = self.apps_registry.get_model("chains", "Feature")

        # Get the chains field
        chains_field = Feature._meta.get_field("chains")

        # Test updated help text
        expected_help_text = "Chains where this feature is enabled. Used only when scope is per-chain."
        self.assertEqual(chains_field.help_text, expected_help_text)
        self.assertTrue(chains_field.blank)

    def test_existing_features_have_default_scope(self) -> None:
        """Test that existing features get the default scope value"""
        Feature = self.apps_registry.get_model("chains", "Feature")

        # Get the existing features
        feature1 = Feature.objects.get(key="test-feature-1")
        feature2 = Feature.objects.get(key="test-feature-2")

        # Both should have the default scope
        self.assertEqual(feature1.scope, "PER_CHAIN")
        self.assertEqual(feature2.scope, "PER_CHAIN")

    def test_existing_chain_relationships_preserved(self) -> None:
        """Test that existing chain relationships are preserved after migration"""
        Feature = self.apps_registry.get_model("chains", "Feature")
        Chain = self.apps_registry.get_model("chains", "Chain")

        # Get the existing features and chains
        feature1 = Feature.objects.get(key="test-feature-1")
        feature2 = Feature.objects.get(key="test-feature-2")
        chain1 = Chain.objects.get(id=1)
        chain2 = Chain.objects.get(id=137)

        # Check that chain relationships are preserved
        self.assertIn(chain1, feature1.chains.all())
        self.assertEqual(feature1.chains.count(), 1)

        self.assertIn(chain1, feature2.chains.all())
        self.assertIn(chain2, feature2.chains.all())
        self.assertEqual(feature2.chains.count(), 2)

    def test_new_feature_with_scope_and_services(self) -> None:
        """Test creating a new feature with scope and services after migration"""
        Feature = self.apps_registry.get_model("chains", "Feature")
        Service = self.apps_registry.get_model("chains", "Service")
        Chain = self.apps_registry.get_model("chains", "Chain")

        # Create a new feature with GLOBAL scope
        global_feature = Feature.objects.create(
            key="global-feature",
            description="A global feature",
            scope="GLOBAL"
        )

        # Add services to the feature
        service1 = Service.objects.get(key="cgw")
        service2 = Service.objects.get(key="frontend")
        global_feature.services.add(service1, service2)

        # Verify the feature
        self.assertEqual(global_feature.scope, "GLOBAL")
        self.assertEqual(global_feature.services.count(), 2)
        self.assertIn(service1, global_feature.services.all())
        self.assertIn(service2, global_feature.services.all())

    def test_scope_choices_validation(self) -> None:
        """Test that scope field validates choices correctly"""
        Feature = self.apps_registry.get_model("chains", "Feature")

        # Test valid choices
        valid_feature_global = Feature.objects.create(
            key="valid-global",
            description="Valid global feature",
            scope="GLOBAL"
        )
        self.assertEqual(valid_feature_global.scope, "GLOBAL")

        valid_feature_per_chain = Feature.objects.create(
            key="valid-per-chain",
            description="Valid per-chain feature",
            scope="PER_CHAIN"
        )
        self.assertEqual(valid_feature_per_chain.scope, "PER_CHAIN")

    def test_services_many_to_many_relationship(self) -> None:
        """Test the M2M relationship between Feature and Service"""
        Feature = self.apps_registry.get_model("chains", "Feature")
        Service = self.apps_registry.get_model("chains", "Service")

        # Create a feature
        feature = Feature.objects.create(
            key="m2m-test-feature",
            description="Feature for M2M testing"
        )

        # Get services
        cgw_service = Service.objects.get(key="cgw")
        frontend_service = Service.objects.get(key="frontend")

        # Test adding services
        feature.services.add(cgw_service)
        self.assertEqual(feature.services.count(), 1)
        self.assertIn(cgw_service, feature.services.all())

        # Test adding multiple services
        feature.services.add(frontend_service)
        self.assertEqual(feature.services.count(), 2)
        self.assertIn(frontend_service, feature.services.all())

        # Test removing services
        feature.services.remove(cgw_service)
        self.assertEqual(feature.services.count(), 1)
        self.assertNotIn(cgw_service, feature.services.all())
        self.assertIn(frontend_service, feature.services.all())

    def test_feature_model_fields_after_migration(self) -> None:
        """Test that all expected fields exist on the Feature model after migration"""
        Feature = self.apps_registry.get_model("chains", "Feature")

        # Get model fields
        field_names = [field.name for field in Feature._meta.get_fields()]

        # Check that all expected fields exist
        expected_fields = ["id", "key", "description", "scope", "chains", "services"]
        for field_name in expected_fields:
            self.assertIn(field_name, field_names)

    def test_blank_services_allowed(self) -> None:
        """Test that features can be created without services (blank=True)"""
        Feature = self.apps_registry.get_model("chains", "Feature")

        # Create a feature without services
        feature = Feature.objects.create(
            key="no-services-feature",
            description="Feature without services"
        )

        # Should have no services
        self.assertEqual(feature.services.count(), 0)

        # Should be able to save without validation errors
        feature.full_clean()  # This would raise ValidationError if blank=False
