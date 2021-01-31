from threading import Lock
from typing import Iterable

from common import Runnable, Printable
from models.client import ClientStorage, Client, ClientListener
from models.server import Server
from utils import delay


class ServerManager(Runnable, Printable):
    def __init__(self, servers: Iterable[Server], storage: ClientStorage, listener: ClientListener) -> None:
        super().__init__()
        self._servers, self._storage, self._listener = servers, storage, listener
        self._should_run = True
        self._lock = Lock()

    def run(self) -> None:
        while self._should_run and self._storage:
            self._process_client_from_queue()
            delay(1)

    def stop(self) -> None:
        self._should_run = False

    def _process_client_from_queue(self):
        with self._lock:
            for server in self._servers:
                if not server.is_working:
                    client = self._storage.pop()
                    if client:
                        self._listener.on_popped_from_queue(client)
                        server.client = client

    def schedule(self, client: Client) -> bool:
        with self._lock:
            scheduled = self._assign_server(client)
            if not scheduled:
                self._queue_client(client)
                self._listener.on_scheduled(client)

            return scheduled

    def _queue_client(self, client: Client) -> None:
        self._storage.add(client)
        self._print(f'{client} has been queued.')
        self._listener.on_queued(client)

    def _assign_server(self, client: Client):
        server = next(filter(lambda h: not h.is_working, self._servers), None)
        if server:
            server.client = client

        return server is not None

    def __str__(self) -> str:
        return self.__class__.__name__
