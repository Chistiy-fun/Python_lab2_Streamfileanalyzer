"""Содержит общие фикстуры для создания тестовых событий."""

from datetime import datetime, timezone

import pytest

from streamstats.models import Event


@pytest.fixture
def event_data() -> dict[str, str]:
    return {
        "timestamp": "2026-10-20T09:00:00+03:00",
        "level": "INFO",
        "source": "api",
        "message": "request completed",
    }


@pytest.fixture
def make_event():
    def factory(
        timestamp: str = "2026-10-20T09:00:00Z",
        level: str = "INFO",
        source: str = "api",
        message: str = "message",
    ) -> Event:
        return Event(
            datetime.fromisoformat(timestamp).astimezone(timezone.utc),
            level,
            source,
            message,
        )

    return factory
