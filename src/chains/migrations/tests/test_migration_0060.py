# SPDX-License-Identifier: FSL-1.1-MIT
import factory
from django.db.migrations.state import StateApps

from chains.migrations.tests.utils import TestMigrations
from chains.tests.factories import ChainFactory

EXPECTED_OPTIONS_BY_RELAYER_TYPE = {
    "DAILY_LIMIT": ["FREE_DAILY_LIMIT"],
    "NO_FEE_CAMPAIGN": ["NO_FEE_CAMPAIGN"],
    "RELAY_FEE": ["PAY_FROM_SAFE"],
    "GTF": [],
    None: [],
}


class Migration0060TestCase(TestMigrations):
    migrate_from = "0059_remove_contract_address_fields"
    migrate_to = "0060_chain_relayer_gas_payment_options"

    def setUpBeforeMigration(self, apps: StateApps) -> None:
        Chain = apps.get_model("chains", "Chain")
        self.chain_ids_by_relayer_type: dict[str | None, int] = {}
        for chain_id, relayer_type in enumerate(EXPECTED_OPTIONS_BY_RELAYER_TYPE):
            # The factory tracks the current model; drop what 0059 lacks.
            attributes = factory.build(
                dict,
                FACTORY_CLASS=ChainFactory,
                id=chain_id,
                relayer_type=relayer_type,
            )
            attributes.pop("relayer_gas_payment_options")
            chain = Chain.objects.create(**attributes)
            self.chain_ids_by_relayer_type[relayer_type] = chain.id

    def test_gas_payment_options_follow_relayer_type(self) -> None:
        Chain = self.apps_registry.get_model("chains", "Chain")
        for relayer_type, expected in EXPECTED_OPTIONS_BY_RELAYER_TYPE.items():
            with self.subTest(relayer_type=relayer_type):
                chain = Chain.objects.get(
                    id=self.chain_ids_by_relayer_type[relayer_type]
                )
                self.assertEqual(chain.relayer_gas_payment_options, expected)

    def test_relayer_type_untouched(self) -> None:
        Chain = self.apps_registry.get_model("chains", "Chain")
        for relayer_type, chain_id in self.chain_ids_by_relayer_type.items():
            with self.subTest(relayer_type=relayer_type):
                self.assertEqual(
                    Chain.objects.get(id=chain_id).relayer_type, relayer_type
                )
