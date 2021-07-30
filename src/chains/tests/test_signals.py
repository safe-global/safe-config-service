from unittest.mock import patch

import responses
from django.test import TestCase, override_settings

from chains.tests.factories import ChainFactory


class ChainHookTestCase(TestCase):
    @patch("requests.sessions.Session.post")
    def test_on_chain_update_with_no_cgw_set(self, mock_post):
        ChainFactory.create()

        assert not mock_post.called

    @patch("requests.sessions.Session.post")
    @override_settings(
        CGW_URL="http://127.0.0.1",
    )
    def test_on_chain_update_with_no_flush_token_set(self, mock_post):
        ChainFactory.create()

        assert not mock_post.called


@override_settings(
    CGW_URL="http://127.0.0.1",
    CGW_FLUSH_TOKEN="example-token",
)
class ChainNetworkHookTestCase(TestCase):
    @responses.activate
    def test_on_chain_update_hook_200(self):
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/flush/example-token",
            status=200,
            match=[responses.json_params_matcher({"invalidate": "Chains"})],
        )

        ChainFactory.create()

        assert len(responses.calls) == 1
        assert responses.calls[0].request.body == b'{"invalidate": "Chains"}'
        assert (
            responses.calls[0].request.url == "http://127.0.0.1/v1/flush/example-token"
        )

    @responses.activate
    def test_on_chain_update_hook_400(self):
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/flush/example-token",
            status=400,
            match=[responses.json_params_matcher({"invalidate": "Chains"})],
        )

        ChainFactory.create()

        assert len(responses.calls) == 1

    @responses.activate
    def test_on_chain_update_hook_500(self):
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/flush/example-token",
            status=500,
            match=[responses.json_params_matcher({"invalidate": "Chains"})],
        )

        ChainFactory.create()

        assert len(responses.calls) == 1

    @responses.activate
    def test_on_chain_delete_hook_call(self):
        chain = ChainFactory.create()

        chain.delete()

        # 2 calls: one for creation and one for deletion
        assert len(responses.calls) == 2

    @responses.activate
    def test_on_chain_update_hook_call(self):
        chain = ChainFactory.create()

        # Not updating using queryset because hooks are not triggered that way
        chain.currency_name = "Ether"
        chain.save()

        # 2 calls: one for creation and one for updating
        assert len(responses.calls) == 2
