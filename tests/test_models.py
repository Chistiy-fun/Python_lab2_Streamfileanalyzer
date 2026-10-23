"""Проверяет модель Event и валидацию полей и временных меток."""

from datetime import datetime, timezone

import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import Event, parse_timestamp, validate_event


def test_event_is_immutable(make_event) -> None:
    event = make_event()

    with pytest.raises(AttributeError):
        event.level = "ERROR"


def test_validate_event_returns_event(event_data) -> None:
    event = validate_event(event_data)

    assert isinstance(event, Event)
    assert event.level == "INFO"
    assert event.source == "api"


def test_validate_event_accepts_empty_message(event_data) -> None:
    event_data["message"] = ""

    assert validate_event(event_data).message == ""


def test_validate_event_rejects_missing_field(event_data) -> None:
    del event_data["source"]

    with pytest.raises(InvalidEventError, match="Missing required field: source"):
        validate_event(event_data)


def test_validate_event_rejects_non_string_field(event_data) -> None:
    event_data["message"] = 123

    with pytest.raises(InvalidEventError, match="Field message must be a string"):
        validate_event(event_data)


def test_validate_event_rejects_blank_source(event_data) -> None:
    event_data["source"] = "   "

    with pytest.raises(InvalidEventError, match="Field source must not be empty"):
        validate_event(event_data)


def test_parse_timestamp_assumes_utc_for_naive_value() -> None:
    result = parse_timestamp("2026-10-20T06:00:00")

    assert result == datetime(2026, 10, 20, 6, tzinfo=timezone.utc)


def test_parse_timestamp_rejects_invalid_format() -> None:
    with pytest.raises(InvalidTimestampError):
        parse_timestamp("invalid")
