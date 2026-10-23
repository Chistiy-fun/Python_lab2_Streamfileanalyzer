"""Проверяет регистрацию парсеров и обработку неизвестных форматов."""

import pytest

from streamstats.errors import UnsupportedFileFormatError
from streamstats.registry import PARSERS, get_parser, register_parser


def parser_factory(*args, **kwargs):
    yield from ()


def test_parser_registry_starts_with_no_implicit_entries() -> None:
    assert isinstance(PARSERS, dict)


def test_register_parser_adds_parser() -> None:
    name = "test-add"
    register_parser(name, parser_factory)

    try:
        assert PARSERS[name] is parser_factory
    finally:
        PARSERS.pop(name, None)


def test_register_parser_rejects_duplicate_name() -> None:
    name = "test-duplicate"
    register_parser(name, parser_factory)

    try:
        with pytest.raises(ValueError, match="already registered"):
            register_parser(name, parser_factory)
    finally:
        PARSERS.pop(name, None)


def test_get_parser_returns_registered_parser() -> None:
    name = "test-get"
    register_parser(name, parser_factory)

    try:
        assert get_parser(name) is parser_factory
    finally:
        PARSERS.pop(name, None)


def test_get_parser_rejects_unknown_name() -> None:
    with pytest.raises(UnsupportedFileFormatError, match="not registered"):
        get_parser("unknown-test-format")
