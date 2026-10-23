"""Определяет исключения для ошибок анализа, данных и форматов файлов."""

class StreamStatsError(Exception):
    pass


class InvalidEventError(StreamStatsError):
    pass


class InvalidTimestampError(InvalidEventError):
    pass


class UnsupportedFileFormatError(StreamStatsError):
    pass
