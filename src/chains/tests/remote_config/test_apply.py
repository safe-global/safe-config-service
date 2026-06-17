# SPDX-License-Identifier: FSL-1.1-MIT
from django.contrib.admin.models import ADDITION, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.test import TestCase

from chains.models import Feature, Service
from chains.remote_config.apply import apply_changes
from chains.remote_config.diff import Change, ChangeType, FieldDelta
from chains.remote_config.state import known_chain_ids, load_feature_states

from ..factories import ChainFactory, FeatureFactory, ServiceFactory


def _actor():  # type: ignore[no-untyped-def]
    return get_user_model().objects.create_superuser(
        username="op", email="op@example.test", password="pw"
    )


class LoadStateTestCase(TestCase):
    def test_projects_features_with_chains_and_services(self) -> None:
        chain = ChainFactory()
        service = ServiceFactory(key="WALLET_WEB")
        feature = FeatureFactory(
            key="SPACES",
            scope=Feature.Scope.PER_CHAIN,
            chains=[chain],
            services=[service],
        )

        states = load_feature_states()

        state = states["SPACES"]
        assert state.feature_id == feature.pk
        assert state.chains == frozenset({str(chain.id)})
        assert state.services == frozenset({"WALLET_WEB"})

    def test_known_chain_ids_are_strings(self) -> None:
        chain = ChainFactory()
        assert known_chain_ids() == {str(chain.id)}


class ApplyChangesTestCase(TestCase):
    def test_add_creates_attaches_and_seeds_chains(self) -> None:
        chain = ChainFactory()
        change = Change(
            type=ChangeType.ADD,
            service_key="WALLET_WEB",
            key="NEWFLAG",
            declared_description="A new flag.",
            declared_scope="PER_CHAIN",
            declared_chains=(str(chain.id),),
        )

        result = apply_changes([change], actor=_actor())

        feature = Feature.objects.get(key="NEWFLAG")
        assert feature.description == "A new flag."
        assert feature.scope == Feature.Scope.PER_CHAIN
        assert set(feature.services.values_list("key", flat=True)) == {"WALLET_WEB"}
        assert set(feature.chains.values_list("id", flat=True)) == {chain.id}
        assert result.added == 1
        assert LogEntry.objects.filter(action_flag=ADDITION).count() == 1

    def test_add_auto_creates_missing_service(self) -> None:
        change = Change(
            type=ChangeType.ADD,
            service_key="WALLET_WEB",
            key="GLOBAL_FLAG",
            declared_description="x",
            declared_scope="GLOBAL",
        )

        apply_changes([change], actor=_actor())

        assert Service.objects.filter(key="WALLET_WEB").exists()

    def test_attach_adds_service_to_existing_feature(self) -> None:
        cgw = ServiceFactory(key="CGW")
        web = ServiceFactory(key="WALLET_WEB")
        feature = FeatureFactory(key="SHARED", services=[cgw])

        change = Change(
            type=ChangeType.ATTACH,
            service_key="WALLET_WEB",
            key="SHARED",
            feature_id=feature.pk,
        )
        apply_changes([change], actor=_actor())

        feature.refresh_from_db()
        assert set(feature.services.values_list("key", flat=True)) == {
            "CGW",
            "WALLET_WEB",
        }
        assert web  # referenced

    def test_update_applies_only_selected_deltas(self) -> None:
        web = ServiceFactory(key="WALLET_WEB")
        feature = FeatureFactory(
            key="X", description="old", scope=Feature.Scope.PER_CHAIN, services=[web]
        )

        change = Change(
            type=ChangeType.UPDATE,
            service_key="WALLET_WEB",
            key="X",
            feature_id=feature.pk,
            deltas=(FieldDelta("description", "old", "new", True),),
        )
        result = apply_changes([change], actor=_actor())

        feature.refresh_from_db()
        assert feature.description == "new"
        assert result.updated == 1

    def test_update_chains_delta_sets_chains(self) -> None:
        web = ServiceFactory(key="WALLET_WEB")
        keep, add = ChainFactory(), ChainFactory()
        feature = FeatureFactory(
            key="X", scope=Feature.Scope.PER_CHAIN, chains=[keep], services=[web]
        )

        change = Change(
            type=ChangeType.UPDATE,
            service_key="WALLET_WEB",
            key="X",
            feature_id=feature.pk,
            deltas=(
                FieldDelta(
                    "chains", (str(keep.id),), (str(keep.id), str(add.id)), False
                ),
            ),
        )
        apply_changes([change], actor=_actor())

        feature.refresh_from_db()
        assert set(feature.chains.values_list("id", flat=True)) == {keep.id, add.id}

    def test_detach_removes_service_keeps_feature(self) -> None:
        cgw = ServiceFactory(key="CGW")
        web = ServiceFactory(key="WALLET_WEB")
        feature = FeatureFactory(key="SHARED", services=[cgw, web])

        change = Change(
            type=ChangeType.DETACH,
            service_key="WALLET_WEB",
            key="SHARED",
            feature_id=feature.pk,
            remaining_services_after=1,
        )
        result = apply_changes([change], actor=_actor())

        feature.refresh_from_db()
        assert set(feature.services.values_list("key", flat=True)) == {"CGW"}
        assert result.detached == 1

    def test_delete_removes_feature_row(self) -> None:
        web = ServiceFactory(key="WALLET_WEB")
        feature = FeatureFactory(key="DEAD", services=[web])

        change = Change(
            type=ChangeType.DELETE,
            service_key="WALLET_WEB",
            key="DEAD",
            feature_id=feature.pk,
            remaining_services_after=0,
        )
        result = apply_changes([change], actor=_actor())

        assert not Feature.objects.filter(key="DEAD").exists()
        assert result.deleted == 1
        assert LogEntry.objects.filter(action_flag=DELETION).count() == 1

    def test_is_transactional_on_error(self) -> None:
        good = Change(
            type=ChangeType.ADD,
            service_key="WALLET_WEB",
            key="GOOD",
            declared_description="x",
            declared_scope="GLOBAL",
        )
        # feature_id that does not exist -> Feature.DoesNotExist mid-transaction.
        bad = Change(
            type=ChangeType.UPDATE,
            service_key="WALLET_WEB",
            key="MISSING",
            feature_id=999999,
            deltas=(FieldDelta("description", "a", "b", True),),
        )

        with self.assertRaises(Feature.DoesNotExist):
            apply_changes([good, bad], actor=_actor())

        # The whole transaction rolled back: GOOD must not persist.
        assert not Feature.objects.filter(key="GOOD").exists()
