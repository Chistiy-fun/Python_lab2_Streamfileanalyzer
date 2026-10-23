"""Хранит зарегистрированные парсеры и предоставляет доступ к ним по имени."""

from collections.abc import Callable, Iterator

from streamstats.errors import UnsupportedFileFormatError
from streamstats.models import Event

Parser = Callable[..., Iterator[Event]]

PARSERS: dict[str, Parser] = {}


def register_parser(name: str, parser: Parser) -> None:
    """Вход: имя формата и функция-парсер. Выход: регистрация парсера; None."""
    if name in PARSERS:
        raise ValueError(f"Parser with name '{name}' is already registered.")
    PARSERS[name] = parser


def get_parser(name: str) -> Parser:
    """Вход: имя формата. Выход: зарегистрированная функция-парсер."""
    if name not in PARSERS:
        raise UnsupportedFileFormatError(f"Parser with name '{name}' is not registered.")
    return PARSERS[name]
