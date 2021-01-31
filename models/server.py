from multiprocessing.connection import Client
from threading import Lock

from common import Identifiable, Runnable, Printable
from distributions import DistributionGenerator
from event_listener import ListenerManager
from utils import delay, Stopwatch


class Server(Identifiable, Runnable, Printable):
    def __init__(self, generator: DistributionGenerator, eventbus: ListenerManager) -> None:
        super().__init__()
        self._generator, self._listener_manager = generator, eventbus
        self._should_run = True
        self._client = None
        self._lock = Lock()

    @property
    def is_working(self) -> bool:
        return bool(self._client)

    def __bool__(self) -> bool:
        return not self.is_working

    @property
    def client(self) -> Client:
        return self._client

    @client.setter
    def client(self, value: Client) -> None:
        with self._lock:
            self._listener_manager.on_processing_started(value)
            self._client = value

    def _process(self, client: Client) -> None:
        duration = int(next(self._generator))
        self._print(f'processing {client}.')
        stopwatch = Stopwatch()
        delay(duration)

        self._print(f'{client} has been processed for {stopwatch.milliseconds_since_start} milliseconds.')
        self._listener_manager.on_processing_finished(client)

    def run(self):
        self._print('server has been started.')
        while self._should_run:
            if self._client:
                self._process(self._client)
                self._client = None
            delay(1)
        self._print('server has been stopped.')

    def stop(self):
        self._should_run = False
