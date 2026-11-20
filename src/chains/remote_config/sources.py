# SPDX-License-Identifier: FSL-1.1-MIT
"""Declaration sources: where each service's declaration file lives in Git."""
from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class RemoteConfigSource:
    """A single repo/path/service mapping for a declaration file."""

    label: str
    service_key: str
    repo: str
    path: str
    default_ref: str


def get_sources() -> list[RemoteConfigSource]:
    """Return the configured declaration sources from ``REMOTE_CONFIG_SOURCES``."""
    return [
        RemoteConfigSource(
            label=entry["label"],
            service_key=entry["service_key"],
            repo=entry["repo"],
            path=entry["path"],
            default_ref=entry.get("default_ref", "main"),
        )
        for entry in settings.REMOTE_CONFIG_SOURCES
    ]
