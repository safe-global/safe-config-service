# SPDX-License-Identifier: FSL-1.1-MIT
from unittest.mock import MagicMock, patch

from django.contrib.admin.models import ADDITION, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.test import TestCase

from chains.models import Feature, Service
from chains.remote_config.apply import apply_changes
from chains.remote_config.diff import Change, ChangeType, FieldDelta, FieldName
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

    def test_add_is_idempotent_for_key_shared_across_services(self) -> None:
        # The same key declared by two services is proposed as ADD for each
        # (per-service diff over one snapshot). Applying both must not collide.
        web_add = Change(
            type=ChangeType.ADD,
            service_key="WALLET_WEB",
            key="DEFAULT_TOKENLIST",
            declared_description="Curated default token list.",
            declared_scope="PER_CHAIN",
        )
        mobile_add = Change(
            type=ChangeType.ADD,
            service_key="MOBILE",
            key="DEFAULT_TOKENLIST",
            declared_description="Curated default token list.",
            declared_scope="PER_CHAIN",
        )

        result = apply_changes([web_add, mobile_add], actor=_actor())

        feature = Feature.objects.get(key="DEFAULT_TOKENLIST")
        assert set(feature.services.values_list("key", flat=True)) == {
            "WALLET_WEB",
            "MOBILE",
        }
        assert result.added == 1
        assert result.attached == 1

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
            deltas=(FieldDelta(FieldName.DESCRIPTION, "old", "new", True),),
        )
        result = apply_changes([change], actor=_actor())

        feature.refresh_from_db()
        assert feature.description == "new"
        assert result.updated == 1

    def test_update_skips_a_description_changed_after_the_diff(self) -> None:
        web = ServiceFactory(key="WALLET_WEB")
        feature = FeatureFactory(
            key="X", description="edited by hand", scope=Feature.Scope.PER_CHAIN, services=[web]
        )
        change = Change(
            type=ChangeType.UPDATE,
            service_key="WALLET_WEB",
            key="X",
            feature_id=feature.pk,
            deltas=(FieldDelta(FieldName.DESCRIPTION, "old", "new", True),),
        )

        result = apply_changes([change], actor=_actor())

        feature.refresh_from_db()
        assert feature.description == "edited by hand"
        assert (result.updated, result.skipped) == (0, 1)

    def test_update_skips_chains_changed_after_the_diff(self) -> None:
        web = ServiceFactory(key="WALLET_WEB")
        seen, added_later, declared = ChainFactory(), ChainFactory(), ChainFactory()
        feature = FeatureFactory(
            key="X",
            scope=Feature.Scope.PER_CHAIN,
            chains=[seen, added_later],
            services=[web],
        )
        change = Change(
            type=ChangeType.UPDATE,
            service_key="WALLET_WEB",
            key="X",
            feature_id=feature.pk,
            deltas=(
                FieldDelta(FieldName.CHAINS, (str(seen.id),), (str(declared.id),), False),
            ),
        )

        result = apply_changes([change], actor=_actor())

        assert set(feature.chains.values_list("id", flat=True)) == {seen.id, added_later.id}
        assert result.skipped == 1

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
                    FieldName.CHAINS, (str(keep.id),), (str(keep.id), str(add.id)), False
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

    def test_delete_keeps_feature_when_a_service_attached_after_the_diff(self) -> None:
        web = ServiceFactory(key="WALLET_WEB")
        feature = FeatureFactory(key="SHARED", services=[web])
        change = Change(
            type=ChangeType.DELETE,
            service_key="WALLET_WEB",
            key="SHARED",
            feature_id=feature.pk,
            remaining_services_after=0,
        )
        feature.services.add(ServiceFactory(key="MOBILE"))

        result = apply_changes([change], actor=_actor())

        feature.refresh_from_db()
        assert set(feature.services.values_list("key", flat=True)) == {"MOBILE"}
        assert result.deleted == 0
        assert result.detached == 1

    def test_flag_moved_between_services_survives_in_any_selection_order(self) -> None:
        chain = ChainFactory()
        web = ServiceFactory(key="WALLET_WEB")
        ServiceFactory(key="MOBILE")
        feature = FeatureFactory(key="MOVED", services=[web], chains=[chain])
        delete_from_web = Change(
            type=ChangeType.DELETE,
            service_key="WALLET_WEB",
            key="MOVED",
            feature_id=feature.pk,
            remaining_services_after=0,
        )
        attach_mobile = Change(
            type=ChangeType.ATTACH, service_key="MOBILE", key="MOVED", feature_id=feature.pk
        )

        apply_changes([delete_from_web, attach_mobile], actor=_actor())

        feature.refresh_from_db()
        assert set(feature.services.values_list("key", flat=True)) == {"MOBILE"}
        assert list(feature.chains.all()) == [chain]

    def test_detaching_every_service_in_one_batch_deletes_the_row(self) -> None:
        web = ServiceFactory(key="WALLET_WEB")
        mobile = ServiceFactory(key="MOBILE")
        feature = FeatureFactory(key="UNUSED", services=[web, mobile])
        changes = [
            Change(
                type=ChangeType.DETACH,
                service_key=service_key,
                key="UNUSED",
                feature_id=feature.pk,
                remaining_services_after=1,
            )
            for service_key in ("WALLET_WEB", "MOBILE")
        ]

        result = apply_changes(changes, actor=_actor())

        assert not Feature.objects.filter(key="UNUSED").exists()
        assert result.detached == 1
        assert result.deleted == 1

    def test_is_transactional_on_error(self) -> None:
        good = Change(
            type=ChangeType.ADD,
            service_key="WALLET_WEB",
            key="GOOD",
            declared_description="x",
            declared_scope="GLOBAL",
        )
        # An UPDATE without feature_id is a programming error -> ValueError mid-transaction.
        bad = Change(
            type=ChangeType.UPDATE,
            service_key="WALLET_WEB",
            key="MISSING",
            deltas=(FieldDelta(FieldName.DESCRIPTION, "a", "b", True),),
        )

        with self.assertRaises(ValueError):
            apply_changes([good, bad], actor=_actor())

        # The whole transaction rolled back: GOOD must not persist.
        assert not Feature.objects.filter(key="GOOD").exists()

    def test_skips_changes_for_a_feature_deleted_after_the_diff(self) -> None:
        feature = FeatureFactory(key="GONE", services=[ServiceFactory(key="WALLET_WEB")])
        stale_id = feature.pk
        feature.delete()
        changes = [
            Change(type=change_type, service_key="WALLET_WEB", key="GONE", feature_id=stale_id)
            for change_type in (
                ChangeType.ATTACH,
                ChangeType.UPDATE,
                ChangeType.DETACH,
                ChangeType.DELETE,
            )
        ]

        result = apply_changes(changes, actor=_actor())

        assert result.skipped == 4
        assert result.total == 0
        assert LogEntry.objects.count() == 0

    def test_skips_detach_when_service_row_is_missing(self) -> None:
        feature = FeatureFactory(key="KEEP", services=[ServiceFactory(key="CGW")])
        change = Change(
            type=ChangeType.DETACH,
            service_key="WALLET_WEB",
            key="KEEP",
            feature_id=feature.pk,
            remaining_services_after=1,
        )

        result = apply_changes([change], actor=_actor())

        assert result.skipped == 1
        assert result.detached == 0
        assert list(feature.services.values_list("key", flat=True)) == ["CGW"]


class ApplyWebhookTestCase(TestCase):
    @patch("chains.services.hook_event")
    def test_sends_each_chain_and_service_hook_once_after_commit(
        self, hook_event: MagicMock
    ) -> None:
        first, second = ChainFactory(), ChainFactory()
        changes = [
            Change(
                type=ChangeType.ADD,
                service_key="WALLET_WEB",
                key=key,
                declared_description=key,
                declared_scope="GLOBAL",
            )
            for key in ("ONE", "TWO")
        ]
        hook_event.reset_mock()

        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            apply_changes(changes, actor=_actor())
        assert hook_event.call_count == 0

        for callback in callbacks:
            callback()

        sent = [(call.args[0].chain_id, call.args[0].service) for call in hook_event.call_args_list]
        chain_ids = {first.id, second.id}
        assert len(sent) == len(set(sent))
        assert set(sent) == {
            (chain_id, service) for chain_id in chain_ids for service in (None, "WALLET_WEB")
        }
