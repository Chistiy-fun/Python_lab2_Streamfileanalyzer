"""Накапливает статистику событий и подсчитывает ошибки по источникам."""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from streamstats.models import Event


@dataclass
class Stats:
    total_records: int = 0
    total_events: int = 0
    skipped_invalid: int = 0
    counts_by_level: Counter[str] = field(default_factory=Counter)
    counts_by_source: Counter[str] = field(default_factory=Counter)
    error_counts_by_source: Counter[str] = field(default_factory=Counter)
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None


    def add(self, event: Event) -> None:
        """Вход: объект Event. Выход: обновлённая статистика; возвращает None."""
        self.total_events += 1
        self.counts_by_level[event.level] += 1
        self.counts_by_source[event.source] += 1
        if event.level in ("ERROR", "CRITICAL"):
            self.error_counts_by_source[event.source] += 1
        if self.first_timestamp is None or event.timestamp < self.first_timestamp:
            self.first_timestamp = event.timestamp
        if self.last_timestamp is None or event.timestamp > self.last_timestamp:
            self.last_timestamp = event.timestamp


    def record_invalid(self) -> None:
        """Вход: отсутствует. Выход: увеличенный счётчик ошибок; возвращает None."""
        self.skipped_invalid += 1
        print(f"Skipped invalid event. Total skipped: {self.skipped_invalid}")


    def top_error_sources(self, n: int = 5) -> list[tuple[str, int]]:
        """Вход: число источников n. Выход: список источников с ошибками."""
        return self.error_counts_by_source.most_common(n)
