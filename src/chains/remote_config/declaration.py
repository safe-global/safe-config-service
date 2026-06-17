# SPDX-License-Identifier: FSL-1.1-MIT
"""Pure parsing + validation of remote-config declaration documents.

No Django imports: this module is unit-testable in isolation with only
``jsonschema`` installed.
"""
import json
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).with_name("remote-config.schema.json")


class DeclarationError(Exception):
    """A declaration document could not be parsed or validated."""


@cache
def _validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text())
    return Draft202012Validator(schema)


@dataclass(frozen=True)
class FeatureDecl:
    """A single declared feature flag."""

    key: str
    description: str
    scope: str
    default_chains: tuple[str, ...] = ()


@dataclass(frozen=True)
class Declaration:
    """A parsed, schema-valid declaration file for one service."""

    service: str
    features: tuple[FeatureDecl, ...] = field(default_factory=tuple)

    def keys(self) -> set[str]:
        return {f.key for f in self.features}


def parse_declaration(document: Any) -> Declaration:
    """Validate ``document`` against the schema and return a typed Declaration.

    Args:
        document: The decoded JSON of a declaration file.

    Returns:
        A :class:`Declaration` with one :class:`FeatureDecl` per entry.

    Raises:
        DeclarationError: If the document is not a dict, fails schema
            validation, or contains duplicate feature keys.
    """
    if not isinstance(document, dict):
        raise DeclarationError(
            f"Declaration must be a JSON object, got {type(document).__name__}"
        )

    errors = sorted(_validator().iter_errors(document), key=lambda e: e.path)
    if errors:
        details = "; ".join(
            f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in errors
        )
        raise DeclarationError(f"Declaration failed schema validation: {details}")

    features = tuple(
        FeatureDecl(
            key=entry["key"],
            description=entry["description"],
            scope=entry["scope"],
            default_chains=tuple(entry.get("defaultChains", [])),
        )
        for entry in document["features"]
    )

    seen: set[str] = set()
    duplicates: set[str] = set()
    for feature in features:
        if feature.key in seen:
            duplicates.add(feature.key)
        seen.add(feature.key)
    if duplicates:
        raise DeclarationError(
            f"Duplicate feature keys: {', '.join(sorted(duplicates))}"
        )

    return Declaration(service=document["service"], features=features)


def parse_declaration_text(text: str) -> Declaration:
    """Decode JSON ``text`` then parse it as a declaration.

    Raises:
        DeclarationError: If the text is not valid JSON or fails validation.
    """
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise DeclarationError(f"Declaration is not valid JSON: {error}") from error
    return parse_declaration(document)
