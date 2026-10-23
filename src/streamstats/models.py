"""Содержит модель события и функции проверки входных данных."""

from dataclasses import dataclass
from datetime import datetime, timezone

from streamstats.errors import InvalidEventError, InvalidTimestampError


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    level: str
    source: str
    message: str



def validate_event(raw: dict[str, object]) -> Event:
    """Вход: словарь с данными события. Выход: проверенный объект Event."""
    required_fields = ("timestamp", "level", "source", "message")
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    validated: dict[str, str] = {}

    for field in required_fields:
        if field not in raw:
            raise InvalidEventError(f"Missing required field: {field}")

        value = raw[field]
        if not isinstance(value, str):
            raise InvalidEventError(f"Field {field} must be a string")

        if field == "level" and value not in levels:
            raise InvalidEventError(f"Field {field} must be one of: {', '.join(levels)}")

        if field == "source" and value.strip() == "":
            raise InvalidEventError(f"Field {field} must not be empty")

        validated[field] = value

    return Event(
        timestamp=parse_timestamp(validated["timestamp"]),
        level=validated["level"],
        source=validated["source"],
        message=validated["message"]
    )


def parse_timestamp(value: str) -> datetime:
    """Вход: timestamp в ISO-формате. Выход: datetime в часовом поясе UTC."""
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise InvalidTimestampError(f"Invalid timestamp format: {value}") from error

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)
