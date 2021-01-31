from dataclasses import dataclass
from enum import IntEnum, auto, unique
from statistics import mean

from models.client import Client
from utils import Stopwatch


@dataclass
class TimeMetric:
    client: Client
    time: float


class AverageMetric:
    def __init__(self):
        self._values = []

    def add(self, value: int) -> None:
        self._values.append(value)

    @property
    def average(self) -> int:
        return mean(self._values or [0])


@unique
class SystemState(IntEnum):
    IDLE = auto()
    BUSY = auto()


class SystemMetric:
    def __init__(self) -> None:
        self._state_changes = []
        self._stopwatch = Stopwatch()
        self._current_state = SystemState.IDLE

    def record_idle(self):
        if self._current_state is SystemState.BUSY:
            elapsed = self._stopwatch.milliseconds_since_start
            self._state_changes.append((self._current_state, elapsed))
            self._current_state = SystemState.IDLE
            self._stopwatch = Stopwatch()

    def record_busy(self):
        if self._current_state is SystemState.IDLE:
            elapsed = self._stopwatch.milliseconds_since_start
            self._state_changes.append((self._current_state, elapsed))
            self._current_state = SystemState.BUSY
            self._stopwatch = Stopwatch()

    def stop_record(self):
        elapsed = self._stopwatch.milliseconds_since_start
        state = self._current_state
        self._state_changes.append((state, elapsed))
        self._current_state = None
        self._stopwatch = None

    def idle_time(self):
        idle_states = filter(lambda state_change: state_change[0] is SystemState.IDLE, self._state_changes)
        return sum(map(lambda x: x[1], idle_states))

    def busy_time(self):
        busy_states = filter(lambda state_change: state_change[0] is SystemState.BUSY, self._state_changes)
        return sum(map(lambda x: x[1], busy_states))
