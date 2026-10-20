
class StreamStatsError(Exception):
    pass


class InvalidEventError(StreamStatsError):
    pass


class InvalidTimestampError(InvalidEventError):
    pass
