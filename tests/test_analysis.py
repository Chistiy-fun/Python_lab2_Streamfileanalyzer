"""Проверяет накопление статистики и поиск источников ошибок."""

from streamstats.analysis import Stats


def test_stats_starts_empty() -> None:
    stats = Stats()

    assert stats.total_events == 0
    assert stats.skipped_invalid == 0
    assert stats.first_timestamp is None
    assert stats.last_timestamp is None


def test_add_increments_total_and_level_count(make_event) -> None:
    stats = Stats()

    stats.add(make_event(level="WARNING"))

    assert stats.total_events == 1
    assert stats.counts_by_level == {"WARNING": 1}


def test_add_counts_sources(make_event) -> None:
    stats = Stats()
    stats.add(make_event(source="api"))
    stats.add(make_event(source="worker"))
    stats.add(make_event(source="api"))

    assert stats.counts_by_source == {"api": 2, "worker": 1}


def test_add_counts_only_error_levels(make_event) -> None:
    stats = Stats()
    stats.add(make_event(level="INFO", source="api"))
    stats.add(make_event(level="ERROR", source="api"))
    stats.add(make_event(level="CRITICAL", source="db"))

    assert stats.error_counts_by_source == {"api": 1, "db": 1}


def test_add_tracks_earliest_and_latest_timestamp(make_event) -> None:
    stats = Stats()
    stats.add(make_event(timestamp="2026-10-20T10:00:00Z"))
    stats.add(make_event(timestamp="2026-10-20T08:00:00Z"))
    stats.add(make_event(timestamp="2026-10-20T09:00:00Z"))

    assert stats.first_timestamp is not None
    assert stats.last_timestamp is not None
    assert stats.first_timestamp.isoformat() == "2026-10-20T08:00:00+00:00"
    assert stats.last_timestamp.isoformat() == "2026-10-20T10:00:00+00:00"


def test_record_invalid_increments_counter(capsys) -> None:
    stats = Stats()

    stats.record_invalid()
    stats.record_invalid()

    assert stats.skipped_invalid == 2
    assert "Total skipped: 2" in capsys.readouterr().out


def test_top_error_sources_limits_results(make_event) -> None:
    stats = Stats()
    for source in ("one", "two", "three"):
        stats.add(make_event(level="ERROR", source=source))

    assert stats.top_error_sources(2) == [("one", 1), ("two", 1)]
