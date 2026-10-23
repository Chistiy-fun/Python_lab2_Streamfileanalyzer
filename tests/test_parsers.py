"""Проверяет чтение корректных и обработку ошибочных JSONL и CSV записей."""

import json

import pytest

from streamstats.errors import InvalidEventError
from streamstats.parsers import parse_csv, parse_jsonl


def test_parse_jsonl_reads_multiple_events(tmp_path, event_data) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(event_data),
                json.dumps({**event_data, "level": "ERROR"}),
            ]
        ),
        encoding="utf-8",
    )

    events = list(parse_jsonl(path))

    assert len(events) == 2
    assert [event.level for event in events] == ["INFO", "ERROR"]


def test_parse_jsonl_rejects_invalid_record_by_default(tmp_path, event_data) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text(
        json.dumps(event_data) + "\nnot-json\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError, match="строка 2"):
        list(parse_jsonl(path))


def test_parse_jsonl_rejects_non_object_json(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(InvalidEventError, match="Должен быть JSON-объект"):
        list(parse_jsonl(path))


def test_parse_jsonl_skips_invalid_records(tmp_path, event_data) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text(
        json.dumps(event_data) + "\n" + json.dumps({"level": "ERROR"}) + "\n",
        encoding="utf-8",
    )
    invalid_count = 0

    def on_invalid() -> None:
        nonlocal invalid_count
        invalid_count += 1

    events = list(parse_jsonl(path, skip_invalid=True, on_invalid=on_invalid))

    assert len(events) == 1
    assert invalid_count == 1


def test_parse_csv_reads_events(tmp_path) -> None:
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T09:00:00+03:00,INFO,api,ok\n",
        encoding="utf-8",
    )

    events = list(parse_csv(path))

    assert len(events) == 1
    assert events[0].message == "ok"


def test_parse_csv_rejects_missing_header(tmp_path) -> None:
    path = tmp_path / "events.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(InvalidEventError, match="не содержит заголовка"):
        list(parse_csv(path))


def test_parse_csv_rejects_missing_required_column(tmp_path) -> None:
    path = tmp_path / "events.csv"
    path.write_text("timestamp,level,source\n", encoding="utf-8")

    with pytest.raises(InvalidEventError, match="обязательного поля: message"):
        list(parse_csv(path))


def test_parse_csv_skips_invalid_rows(tmp_path) -> None:
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "bad,INFO,api,broken\n"
        "2026-10-20T09:00:00Z,INFO,api,ok\n",
        encoding="utf-8",
    )
    invalid_count = 0

    def on_invalid() -> None:
        nonlocal invalid_count
        invalid_count += 1

    events = list(parse_csv(path, skip_invalid=True, on_invalid=on_invalid))

    assert len(events) == 1
    assert invalid_count == 1
