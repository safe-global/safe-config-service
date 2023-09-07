import responses
from django.test import TestCase, override_settings

from safe_apps.models import SafeApp, Tag
from safe_apps.tests.factories import ProviderFactory


@override_settings(
    CGW_URL="http://127.0.0.1",
    CGW_FLUSH_TOKEN="example-token",
)
class SafeAppHookTestCase(TestCase):
    @responses.activate
    def test_on_safe_app_create_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        SafeApp(app_id=1, chain_ids=[1]).save()

        assert len(responses.calls) == 1
        assert isinstance(responses.calls[0], responses.Call)
        assert responses.calls[0].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[0].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_safe_app_update_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        safe_app = SafeApp(app_id=1, chain_ids=[1])
        safe_app.save()  # create
        safe_app.name = "Test app"
        safe_app.save()  # update

        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[1].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[1].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_safe_app_delete_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        safe_app = SafeApp(app_id=1, chain_ids=[1])
        safe_app.save()  # create
        safe_app.delete()  # delete

        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[1].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[1].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )


@override_settings(
    CGW_URL="http://127.0.0.1",
    CGW_FLUSH_TOKEN="example-token",
)
class ProviderHookTestCase(TestCase):
    @responses.activate
    def test_on_provider_create_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        ProviderFactory.create()

        assert len(responses.calls) == 1
        assert isinstance(responses.calls[0], responses.Call)
        assert responses.calls[0].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[0].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_provider_update_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        provider = ProviderFactory.create()  # create
        provider.name = "Test Provider"
        provider.save()  # update

        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[1].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[1].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_provider_delete_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        provider = ProviderFactory.create()  # create
        provider.delete()  # delete

        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[1].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[1].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )


@override_settings(
    CGW_URL="http://127.0.0.1",
    CGW_FLUSH_TOKEN="example-token",
)
class TagHookTestCase(TestCase):
    @responses.activate
    def test_on_tag_create_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        Tag().save()  # create

        assert len(responses.calls) == 1
        assert isinstance(responses.calls[0], responses.Call)
        assert responses.calls[0].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[0].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_tag_update_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        tag = Tag()
        tag.save()  # create
        tag.name = "Test Tag"
        tag.save()  # update

        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[1].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[1].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_tag_delete_hook_call(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v2/flush",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher({"invalidate": "Chains"}),
            ],
        )

        tag = Tag()
        tag.save()  # create
        tag.delete()  # delete

        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[1].request.body == b'{"invalidate": "Chains"}'
        assert responses.calls[1].request.url == "http://127.0.0.1/v2/flush"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )
