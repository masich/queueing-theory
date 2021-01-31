from threading import Lock
from typing import Optional, Iterable

from models.client import ClientListener, Client


class ListenerManager(ClientListener):
    def __init__(self, listeners: Optional[Iterable[ClientListener]] = None):
        self._lock = Lock()
        self._listeners = list(listeners or [])

    def add_listener(self, listener: ClientListener) -> None:
        self._listeners.append(listener)

    def on_arrived(self, client: Client) -> None:
        with self._lock:
            for listener in self._listeners:
                listener.on_arrived(client)

    def on_scheduled(self, client: Client) -> None:
        with self._lock:
            for listener in self._listeners:
                listener.on_scheduled(client)

    def on_queued(self, client: Client) -> None:
        with self._lock:
            for listener in self._listeners:
                listener.on_queued(client)

    def on_popped_from_queue(self, client: Client) -> None:
        with self._lock:
            for listener in self._listeners:
                listener.on_popped_from_queue(client)

    def on_processing_started(self, client: Client) -> None:
        with self._lock:
            for listener in self._listeners:
                listener.on_processing_started(client)

    def on_processing_finished(self, client: Client) -> None:
        with self._lock:
            for listener in self._listeners:
                listener.on_processing_finished(client)

    def on_all_processed(self) -> None:
        with self._lock:
            for listener in self._listeners:
                listener.on_all_processed()
