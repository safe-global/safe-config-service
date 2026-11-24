# SPDX-License-Identifier: FSL-1.1-MIT
"""Fetch a declaration file from GitHub's raw endpoint at a given ref.

This is the only I/O in the package. It returns the raw response body; parsing
and schema validation are the caller's job (see
:func:`chains.remote_config.declaration.parse_declaration_text`).

Mirrors the existing CGW client pattern (``requests`` + settings timeout/token).
"""
import logging
import re

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

RAW_URL = "{base}/{repo}/{ref}/{path}"


class DeclarationFetchError(Exception):
    """A declaration file could not be fetched (network/HTTP error)."""


class DeclarationNotFound(DeclarationFetchError):
    """The declaration file does not exist at the requested ref (HTTP 404)."""


_REF_PATTERN = re.compile(r"[A-Za-z0-9._/-]+")


def _check_ref(ref: str) -> None:
    """Reject a ref that could leave the configured repository once the URL is normalized."""
    segments = ref.split("/")
    if not _REF_PATTERN.fullmatch(ref) or any(s in ("", ".", "..") for s in segments):
        raise DeclarationFetchError(
            f"Invalid Git ref {ref!r}: use a branch, tag or commit SHA "
            "(letters, digits, '.', '_', '-', '/'; no empty, '.' or '..' segments)."
        )


def raw_url(repo: str, ref: str, path: str) -> str:
    """Build the raw file URL for ``repo`` at ``ref`` for ``path``.

    Raises:
        DeclarationFetchError: If ``ref`` is not a plain branch, tag or SHA.
    """
    _check_ref(ref)
    return RAW_URL.format(
        base=settings.REMOTE_CONFIG_RAW_BASE_URL.rstrip("/"),
        repo=repo.strip("/"),
        ref=ref,
        path=path.lstrip("/"),
    )


def fetch_declaration_text(repo: str, ref: str, path: str) -> str:
    """Fetch the raw declaration file body.

    Args:
        repo: ``owner/name`` slug, e.g. ``safe-global/safe-wallet-monorepo``.
        ref: Git branch, tag, or commit SHA.
        path: Repo-relative path to the declaration file.

    Returns:
        The response body as text.

    Raises:
        DeclarationNotFound: The file is missing at the ref (HTTP 404).
        DeclarationFetchError: Any other HTTP or network failure.
    """
    headers = {}
    if settings.REMOTE_CONFIG_GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.REMOTE_CONFIG_GITHUB_TOKEN}"

    url = raw_url(repo, ref, path)
    try:
        response = requests.get(
            url, headers=headers, timeout=settings.REMOTE_CONFIG_TIMEOUT_SECONDS
        )
    except requests.RequestException as error:
        logger.warning("Failed to fetch %s: %s", url, error)
        raise DeclarationFetchError(f"Could not fetch {url}: {error}") from error

    if response.status_code == 404:
        raise DeclarationNotFound(f"{path}@{ref} not found in {repo}")

    if response.status_code != 200:
        raise DeclarationFetchError(
            f"Unexpected status {response.status_code} fetching {url}: "
            f"{response.text[:200]}"
        )

    return response.text
