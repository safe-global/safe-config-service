# SPDX-License-Identifier: FSL-1.1-MIT
import requests
import responses
from django.test import SimpleTestCase, override_settings

from chains.remote_config.github import (
    DeclarationFetchError,
    DeclarationNotFound,
    fetch_declaration_text,
    raw_url,
)

REPO = "safe-global/safe-wallet-monorepo"
PATH = "apps/web/config/remote-config.json"
BASE = "https://raw.example.test"


@override_settings(
    REMOTE_CONFIG_RAW_BASE_URL=BASE,
    REMOTE_CONFIG_TIMEOUT_SECONDS=5,
    REMOTE_CONFIG_GITHUB_TOKEN=None,
)
class FetchDeclarationTextTestCase(SimpleTestCase):
    @responses.activate
    def test_returns_body_on_200(self) -> None:
        url = raw_url(REPO, "main", PATH)
        responses.add(responses.GET, url, status=200, body='{"ok": true}')

        assert fetch_declaration_text(REPO, "main", PATH) == '{"ok": true}'

    @responses.activate
    def test_raises_not_found_on_404(self) -> None:
        responses.add(responses.GET, raw_url(REPO, "missing", PATH), status=404)

        with self.assertRaises(DeclarationNotFound):
            fetch_declaration_text(REPO, "missing", PATH)

    @responses.activate
    def test_raises_fetch_error_on_403_rate_limited(self) -> None:
        responses.add(responses.GET, raw_url(REPO, "main", PATH), status=403)

        with self.assertRaises(DeclarationFetchError):
            fetch_declaration_text(REPO, "main", PATH)

    @responses.activate
    def test_raises_fetch_error_on_500(self) -> None:
        responses.add(responses.GET, raw_url(REPO, "main", PATH), status=500)

        with self.assertRaises(DeclarationFetchError):
            fetch_declaration_text(REPO, "main", PATH)

    @responses.activate
    def test_wraps_network_error(self) -> None:
        responses.add(
            responses.GET,
            raw_url(REPO, "main", PATH),
            body=requests.ConnectionError("boom"),
        )

        with self.assertRaises(DeclarationFetchError):
            fetch_declaration_text(REPO, "main", PATH)

    @responses.activate
    @override_settings(REMOTE_CONFIG_GITHUB_TOKEN="secret-token")
    def test_sends_bearer_token_when_configured(self) -> None:
        responses.add(
            responses.GET,
            raw_url(REPO, "main", PATH),
            status=200,
            body="{}",
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Bearer secret-token"}
                )
            ],
        )

        assert fetch_declaration_text(REPO, "main", PATH) == "{}"


@override_settings(REMOTE_CONFIG_RAW_BASE_URL=BASE)
class RawUrlTestCase(SimpleTestCase):
    def test_builds_url_and_strips_separators(self) -> None:
        assert raw_url("/owner/repo/", "abc123", "/some/path.json") == (
            f"{BASE}/owner/repo/abc123/some/path.json"
        )

    def test_accepts_a_branch_with_slashes(self) -> None:
        assert raw_url("owner/repo", "feat/a-b_1.2", "f.json") == (
            f"{BASE}/owner/repo/feat/a-b_1.2/f.json"
        )

    def test_rejects_a_ref_that_leaves_the_repository(self) -> None:
        for ref in ("../../attacker/repo/main", "main/../x", "./main", "a//b", "/main", "main/"):
            with self.subTest(ref=ref), self.assertRaises(DeclarationFetchError):
                raw_url("owner/repo", ref, "f.json")

    def test_rejects_a_ref_with_url_characters(self) -> None:
        for ref in ("main?x=1", "main#x", "ma in", "main%2F..", ""):
            with self.subTest(ref=ref), self.assertRaises(DeclarationFetchError):
                raw_url("owner/repo", ref, "f.json")
