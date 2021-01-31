import time


def delay(milliseconds: int):
    time.sleep(milliseconds / 1000)


def current_timestamp() -> int:
    return round(time.time() * 1000)


class Stopwatch:
    def __init__(self):
        self._start = current_timestamp()

    @property
    def milliseconds_since_start(self) -> int:
        return current_timestamp() - self._start
