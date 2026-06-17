# SPDX-License-Identifier: FSL-1.1-MIT
"""Pure unit tests for declaration parsing/validation (no Django required)."""
import pytest

from chains.remote_config.declaration import (
    Declaration,
    DeclarationError,
    FeatureDecl,
    parse_declaration,
    parse_declaration_text,
)


def _doc(features: list[dict], service: str = "WALLET_WEB") -> dict:
    return {"service": service, "features": features}


def test_parses_valid_per_chain_and_global() -> None:
    declaration = parse_declaration(
        _doc(
            [
                {
                    "key": "SPACES",
                    "description": "Spaces.",
                    "scope": "PER_CHAIN",
                    "defaultChains": ["1", "11155111"],
                },
                {
                    "key": "CSV_TX_EXPORT",
                    "description": "CSV export.",
                    "scope": "GLOBAL",
                },
            ]
        )
    )

    assert declaration == Declaration(
        service="WALLET_WEB",
        features=(
            FeatureDecl("SPACES", "Spaces.", "PER_CHAIN", ("1", "11155111")),
            FeatureDecl("CSV_TX_EXPORT", "CSV export.", "GLOBAL", ()),
        ),
    )
    assert declaration.keys() == {"SPACES", "CSV_TX_EXPORT"}


def test_ignores_top_level_schema_pointer() -> None:
    declaration = parse_declaration(
        {
            "$schema": "./remote-config.schema.json",
            "service": "CGW",
            "features": [
                {"key": "PORTFOLIO_ENDPOINT", "description": "x", "scope": "PER_CHAIN"}
            ],
        }
    )
    assert declaration.service == "CGW"


def test_rejects_non_dict() -> None:
    with pytest.raises(DeclarationError, match="must be a JSON object"):
        parse_declaration([1, 2, 3])


def test_rejects_global_with_chains() -> None:
    with pytest.raises(DeclarationError, match="schema validation"):
        parse_declaration(
            _doc(
                [
                    {
                        "key": "GLOBAL_FLAG",
                        "description": "x",
                        "scope": "GLOBAL",
                        "defaultChains": ["1"],
                    }
                ]
            )
        )


def test_rejects_unknown_scope() -> None:
    with pytest.raises(DeclarationError, match="schema validation"):
        parse_declaration(
            _doc([{"key": "X", "description": "x", "scope": "SOMETIMES"}])
        )


def test_rejects_lowercase_key() -> None:
    with pytest.raises(DeclarationError, match="schema validation"):
        parse_declaration(
            _doc([{"key": "lowercase", "description": "x", "scope": "GLOBAL"}])
        )


def test_rejects_empty_description() -> None:
    with pytest.raises(DeclarationError, match="schema validation"):
        parse_declaration(
            _doc([{"key": "X", "description": "", "scope": "GLOBAL"}])
        )


def test_rejects_non_numeric_chain_id() -> None:
    with pytest.raises(DeclarationError, match="schema validation"):
        parse_declaration(
            _doc(
                [
                    {
                        "key": "X",
                        "description": "x",
                        "scope": "PER_CHAIN",
                        "defaultChains": ["mainnet"],
                    }
                ]
            )
        )


def test_rejects_additional_properties() -> None:
    with pytest.raises(DeclarationError, match="schema validation"):
        parse_declaration(
            _doc(
                [
                    {
                        "key": "X",
                        "description": "x",
                        "scope": "GLOBAL",
                        "owner": "team-web",
                    }
                ]
            )
        )


def test_rejects_missing_service() -> None:
    with pytest.raises(DeclarationError, match="schema validation"):
        parse_declaration({"features": []})


def test_rejects_duplicate_keys() -> None:
    with pytest.raises(DeclarationError, match="Duplicate feature keys: SPACES"):
        parse_declaration(
            _doc(
                [
                    {"key": "SPACES", "description": "a", "scope": "GLOBAL"},
                    {"key": "SPACES", "description": "b", "scope": "GLOBAL"},
                ]
            )
        )


def test_parse_text_rejects_malformed_json() -> None:
    with pytest.raises(DeclarationError, match="not valid JSON"):
        parse_declaration_text("{not json")


def test_parse_text_happy_path() -> None:
    declaration = parse_declaration_text(
        '{"service": "MOBILE", "features": '
        '[{"key": "SEND_FLOW", "description": "x", "scope": "GLOBAL"}]}'
    )
    assert declaration.service == "MOBILE"
    assert declaration.features[0].key == "SEND_FLOW"
