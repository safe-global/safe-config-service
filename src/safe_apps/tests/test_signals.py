import responses
from django.test import TestCase, override_settings
from faker import Faker

from ..models import SafeApp
from .factories import FeatureFactory, ProviderFactory, SafeAppFactory, TagFactory

fake = Faker()
Faker.seed(0)


@override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN="example-token")
class SafeAppHookTestCase(TestCase):
    @responses.activate
    def test_on_safe_app_create(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/hooks/events",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher(
                    {"type": "SAFE_APPS_UPDATE", "chainId": "1"}
                ),
            ],
        )

        SafeApp(app_id=1, chain_ids=[1]).save()

        assert len(responses.calls) == 1
        assert isinstance(responses.calls[0], responses.Call)
        assert (
            responses.calls[0].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "1"}'
        )
        assert responses.calls[0].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_safe_app_update(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/hooks/events",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher(
                    {"type": "SAFE_APPS_UPDATE", "chainId": "1"}
                ),
            ],
        )

        safe_app = SafeApp(app_id=1, chain_ids=[1])
        safe_app.save()  # create
        safe_app.name = "Test app"
        safe_app.save()  # update

        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert (
            responses.calls[1].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "1"}'
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_safe_app_update_by_adding_chain_ids(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/hooks/events",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher(
                    {"type": "SAFE_APPS_UPDATE", "chainId": "1"}
                ),
            ],
        )

        safe_app = SafeApp(app_id=1, chain_ids=[1])
        safe_app.save()  # create
        safe_app.chain_ids = [1, 2, 3]
        safe_app.save()  # update

        assert len(responses.calls) == 4
        assert isinstance(responses.calls[0], responses.Call)
        assert (
            responses.calls[0].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "1"}'
        )
        assert responses.calls[0].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert isinstance(responses.calls[1], responses.Call)
        assert (
            responses.calls[1].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "1"}'
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert isinstance(responses.calls[2], responses.Call)
        assert (
            responses.calls[2].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "2"}'
        )
        assert responses.calls[2].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[2].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert isinstance(responses.calls[3], responses.Call)
        assert (
            responses.calls[3].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "3"}'
        )
        assert responses.calls[3].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[3].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_safe_app_update_by_removing_chain_ids(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/hooks/events",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher(
                    {"type": "SAFE_APPS_UPDATE", "chainId": "1"}
                ),
            ],
        )

        safe_app = SafeApp(app_id=1, chain_ids=[1, 2, 3])
        safe_app.save()  # create
        safe_app.chain_ids = [1]
        safe_app.save()  # update

        assert len(responses.calls) == 6
        assert isinstance(responses.calls[0], responses.Call)
        assert (
            responses.calls[0].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "1"}'
        )
        assert responses.calls[0].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert isinstance(responses.calls[1], responses.Call)
        assert (
            responses.calls[1].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "2"}'
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert isinstance(responses.calls[2], responses.Call)
        assert (
            responses.calls[2].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "3"}'
        )
        assert responses.calls[2].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[2].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert isinstance(responses.calls[3], responses.Call)
        assert (
            responses.calls[3].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "1"}'
        )
        assert responses.calls[3].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[3].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert isinstance(responses.calls[4], responses.Call)
        assert (
            responses.calls[4].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "2"}'
        )
        assert responses.calls[4].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[4].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert isinstance(responses.calls[5], responses.Call)
        assert (
            responses.calls[5].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "3"}'
        )
        assert responses.calls[5].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[5].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_safe_app_delete(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/hooks/events",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher(
                    {"type": "SAFE_APPS_UPDATE", "chainId": "1"}
                ),
            ],
        )

        safe_app = SafeApp(app_id=1, chain_ids=[1])
        safe_app.save()  # create
        safe_app.delete()  # delete

        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert (
            responses.calls[1].request.body
            == b'{"type": "SAFE_APPS_UPDATE", "chainId": "1"}'
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )


@override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN="example-token")
class ProviderHookTestCase(TestCase):
    @responses.activate
    def test_on_provider_create_with_no_safe_app(self) -> None:
        ProviderFactory.create()

        assert len(responses.calls) == 0

    @responses.activate
    def test_on_provider_create_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        provider = ProviderFactory.create()
        SafeAppFactory.create(chain_ids=[chain_id], provider=provider)

        # Safe App Creation, Safe App Update
        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[
            1
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_provider_update_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        provider = ProviderFactory.create()
        SafeAppFactory.create(chain_ids=[chain_id], provider=provider)

        provider.name = "New name"
        provider.save()

        # Safe App Creation, Safe App Update, Provider update
        assert len(responses.calls) == 3
        assert isinstance(responses.calls[2], responses.Call)
        assert responses.calls[
            2
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[2].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[2].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_provider_delete_with_no_safe_app(self) -> None:
        provider = ProviderFactory.create()  # create
        provider.delete()  # delete

        assert len(responses.calls) == 0

    @responses.activate
    def test_on_provider_delete_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        provider = ProviderFactory.create()
        SafeAppFactory.create(chain_ids=[chain_id], provider=provider)

        provider.delete()

        # Safe App Creation, Safe App Update, Provider update
        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[
            1
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )


@override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN="example-token")
class TagHookTestCase(TestCase):
    @responses.activate
    def test_on_tag_create_with_no_safe_app(self) -> None:
        TagFactory.create()  # create

        assert len(responses.calls) == 0

    @responses.activate
    def test_on_tag_create_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        safe_app = SafeAppFactory.create(chain_ids=[chain_id])

        TagFactory.create(safe_apps=(safe_app,))

        # Safe App Creation, Safe App Update, M2M update, Tag create
        assert len(responses.calls) == 4
        assert isinstance(responses.calls[3], responses.Call)
        assert responses.calls[
            3
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )

    @responses.activate
    def test_on_tag_update_with_no_safe_app(self) -> None:
        tag = TagFactory.create()  # create
        tag.name = "Test Tag"

        tag.save()  # update

        assert len(responses.calls) == 0

    @responses.activate
    def test_on_tag_update_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        safe_app = SafeAppFactory.create(chain_ids=[chain_id])
        tag = TagFactory.create(safe_apps=(safe_app,))

        tag.name = "test"
        tag.save()

        # Safe App Creation, Safe App Update, M2M update, Tag create, Tag update
        assert len(responses.calls) == 5
        assert isinstance(responses.calls[4], responses.Call)
        assert responses.calls[
            4
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )

    @responses.activate
    def test_on_tag_delete_with_no_safe_app(self) -> None:
        tag = TagFactory.create()  # create

        tag.delete()  # delete

        assert len(responses.calls) == 0

    @responses.activate
    def test_on_tag_delete_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        safe_app = SafeAppFactory.create(chain_ids=[chain_id])
        tag = TagFactory.create(safe_apps=(safe_app,))

        tag.delete()

        # Safe App Creation, Safe App Update, M2M update, Tag create, Tag delete
        assert len(responses.calls) == 5
        assert isinstance(responses.calls[4], responses.Call)
        assert responses.calls[
            4
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )

    # Otherwise fails when testing with all suites
    # TODO: above tests somehow leak
    @responses.stop  # type: ignore
    @responses.activate
    def test_on_tag_update_with_multiple_safe_apps(self) -> None:
        chain_id_1 = fake.pyint()
        chain_id_2 = fake.pyint()
        safe_app = SafeAppFactory.create(chain_ids=[chain_id_1, chain_id_2])

        TagFactory.create(safe_apps=(safe_app,))

        # Safe App Creation for chain 1, Safe App Creation for chain 2,
        # Safe App Update for chain 1, Safe App Update for chain 2,
        # Tag update for chain 1, M2M update for chain 1
        # Tag update for chain 2, M2M update for chain 2
        assert len(responses.calls) == 8
        assert isinstance(responses.calls[5], responses.Call)
        assert responses.calls[
            4
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id_1}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[
            5
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id_2}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[
            6
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id_1}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[
            7
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id_2}"}}'.encode(
            "utf-8"
        )


@override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN="example-token")
class FeatureHookTestCase(TestCase):
    @responses.activate
    def test_on_feature_create_with_no_safe_app(self) -> None:
        FeatureFactory.create()  # create

        assert len(responses.calls) == 0

    @responses.activate
    def test_on_feature_create_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        safe_app = SafeAppFactory.create(chain_ids=[chain_id])

        FeatureFactory.create(safe_apps=(safe_app,))

        # Safe App Creation, Safe App Update, M2M update, Feature create
        assert len(responses.calls) == 4
        assert isinstance(responses.calls[3], responses.Call)
        assert responses.calls[
            3
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )

    @responses.activate
    def test_on_feature_update_with_no_safe_app(self) -> None:
        feature = FeatureFactory.create()  # create
        feature.name = "Test Feature"

        feature.save()  # update

        assert len(responses.calls) == 0

    @responses.activate
    def test_on_feature_update_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        safe_app = SafeAppFactory.create(chain_ids=[chain_id])
        feature = FeatureFactory.create(safe_apps=(safe_app,))

        feature.name = "test"
        feature.save()

        # Safe App Creation, Safe App Update, M2M update, Feature create, Feature update
        assert len(responses.calls) == 5
        assert isinstance(responses.calls[4], responses.Call)
        assert responses.calls[
            4
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )

    @responses.activate
    def test_on_feature_delete_with_no_safe_app(self) -> None:
        feature = FeatureFactory.create()  # create

        feature.delete()  # delete

        assert len(responses.calls) == 0

    @responses.activate
    def test_on_feature_delete_with_safe_app(self) -> None:
        chain_id = fake.pyint()
        safe_app = SafeAppFactory.create(chain_ids=[chain_id])
        feature = FeatureFactory.create(safe_apps=(safe_app,))

        feature.delete()

        # Safe App Creation, Safe App Update, M2M update, Feature create, Feature delete
        assert len(responses.calls) == 5
        assert isinstance(responses.calls[4], responses.Call)
        assert responses.calls[
            4
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )

    # Otherwise fails when testing with all suites
    # TODO: above tests somehow leak
    @responses.stop  # type: ignore
    @responses.activate
    def test_on_feature_update_with_multiple_safe_apps(self) -> None:
        chain_id_1 = fake.pyint()
        chain_id_2 = fake.pyint()
        safe_app = SafeAppFactory.create(chain_ids=[chain_id_1, chain_id_2])

        FeatureFactory.create(safe_apps=(safe_app,))

        # Safe App Creation for chain 1, Safe App Creation for chain 2,
        # Safe App Update for chain 1, Safe App Update for chain 2,
        # Feature update for chain 1, M2M update for chain 1
        # Feature update for chain 2, M2M update for chain 2
        assert len(responses.calls) == 8
        assert isinstance(responses.calls[5], responses.Call)
        assert responses.calls[
            4
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id_1}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[
            5
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id_2}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[
            6
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id_1}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[
            7
        ].request.body == f'{{"type": "SAFE_APPS_UPDATE", "chainId": "{chain_id_2}"}}'.encode(
            "utf-8"
        )
