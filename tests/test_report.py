"""Проверяет создание и запись отчётов в JSON и CSV."""

import csv
import json

from streamstats.analysis import Stats
from streamstats.report import build_report, write_csv_report, write_json_report


def test_build_report_contains_empty_state() -> None:
    report = build_report(Stats())

    assert report["total_records"] == 0
    assert report["total_events"] == 0
    assert report["first_timestamp"] is None
    assert report["last_timestamp"] is None


def test_build_report_includes_skipped_records(make_event) -> None:
    stats = Stats(skipped_invalid=2)
    stats.add(make_event())

    report = build_report(stats)

    assert report["total_records"] == 3
    assert report["skipped_invalid"] == 2


def test_build_report_serializes_statistics(make_event) -> None:
    stats = Stats()
    stats.add(make_event(level="ERROR", source="db"))

    report = build_report(stats)

    assert report["counts_by_level"] == {"ERROR": 1}
    assert report["error_counts_by_source"] == {"db": 1}
    assert report["top_error_sources"] == [("db", 1)]


def test_write_json_report_writes_utf8_json(tmp_path, make_event) -> None:
    stats = Stats()
    stats.add(make_event(message="ошибка"))
    path = tmp_path / "report.json"

    write_json_report(build_report(stats), path)

    content = path.read_text(encoding="utf-8")
    assert json.loads(content)["total_events"] == 1
    assert "ошибка" not in content


def test_write_csv_report_writes_summary_and_sources(tmp_path, make_event) -> None:
    stats = Stats()
    stats.add(make_event(level="ERROR", source="db"))
    path = tmp_path / "report.csv"

    write_csv_report(build_report(stats), path)

    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))
    assert rows[0] == ["section", "key", "value"]
    assert ["summary", "total_events", "1"] in rows
    assert ["counts_by_source", "db", "1"] in rows
