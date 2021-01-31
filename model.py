from threading import Thread
from typing import Iterable

from common import Printable
from distributions import DistributionGenerator
from models.client import ClientGenerator, ClientListener
from models.manager import ServerManager
from models.server import Server
from utils import Stopwatch, delay


class ImitationModel(Printable):
    def __init__(self, client_distribution: DistributionGenerator, client_generator: ClientGenerator, duration: int,
                 servers: Iterable[Server], manager: ServerManager, listener: ClientListener):
        self._client_generator, self._client_distribution = client_generator, client_distribution
        self._duration, self._servers, self._listener, self._manager = duration, servers, listener, manager
        self._threads = None
        self._manager_thread = None

    def run(self) -> None:
        self._threads = [Thread(target=server.run, name=str(server.id)) for server in self._servers]
        self._manager_thread = Thread(target=self._manager.run)
        self._manager_thread.start()

        for thread in self._threads:
            thread.start()

        self._start()

    def _start(self):
        stopwatch = Stopwatch()
        while stopwatch.milliseconds_since_start < self._duration:
            interval = int(next(self._client_distribution))
            delay(interval)

            client = next(self._client_generator)
            self._listener.on_arrived(client)
            self._manager.schedule(client)

        self._stop()
        self._listener.on_all_processed()
        delay(10)
        self._print(f'stopped after {stopwatch.milliseconds_since_start} milliseconds of simulation.')

    def _stop(self):
        self._manager.stop()
        ImitationModel._wait_for_thread_stop(self._manager_thread)
        self._stop_servers()

    def _stop_servers(self):
        for server in self._servers:
            server.stop()
            self._wait_server_stop(server)

    def _wait_server_stop(self, server: Server):
        thread = next(filter(lambda t: t.name == str(server.id), self._threads))
        ImitationModel._wait_for_thread_stop(thread)

    @staticmethod
    def _wait_for_thread_stop(thread: Thread):
        while thread.is_alive():
            delay(1)
