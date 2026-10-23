"""Читает события из JSONL и CSV и преобразует их в объекты Event."""

import csv
import json
import logging

from streamstats.errors import InvalidEventError
from streamstats.models import validate_event

logger = logging.getLogger(__name__)


def parse_jsonl(path, skip_invalid=False, *, on_invalid=None):
    """Вход: путь к JSONL, флаг пропуска ошибок и callback. Выход: события Event."""
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise InvalidEventError("Должен быть JSON-объект")
                event = validate_event(record)
            except (json.JSONDecodeError ,InvalidEventError) as e:
                if skip_invalid:
                    logger.warning("Файл %s, строка %s: %s", path, line_num, e)

                    if on_invalid is not None:
                        on_invalid()

                    continue
                else:
                    raise InvalidEventError(f"Файл {path}, строка {line_num}: {e}") from e
            yield event


def parse_csv(path, skip_invalid=False, *, on_invalid=None):
    """Вход: путь к CSV, флаг пропуска ошибок и callback. Выход: события Event."""
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise InvalidEventError("CSV-файл не содержит заголовка")

        required_fields = ("timestamp", "level", "source", "message")

        for field in required_fields:
            if field not in reader.fieldnames:
                raise InvalidEventError(f"CSV-файл не содержит обязательного поля: {field}")

        for record in reader:
            try:
                event = validate_event(record)
            except (csv.Error, InvalidEventError) as e:
                if skip_invalid:
                    logger.warning("Файл %s, строка %s: %s", path, reader.line_num, e)

                    if on_invalid is not None:
                        on_invalid()

                    continue
                else:
                    raise InvalidEventError(f"Файл {path}, строка {reader.line_num}: {e}") from e
            yield event
