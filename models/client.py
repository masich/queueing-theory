from abc import ABCMeta, abstractmethod
from collections import deque
from dataclasses import dataclass
from threading import Lock
from typing import Deque, Optional, Iterator

from common import Printable, Identifiable


@dataclass
class Client(Identifiable):
    def __init__(self) -> None:
        super().__init__()


class ClientGenerator(Iterator, Printable):
    def __next__(self) -> Client:
        task = Client()
        self._print(f'{task} has been generated.')
        return task


class ClientStorage:
    def __init__(self, queue_size: Optional[int] = None):
        self._lock = Lock()
        self._queue: Deque[Client] = deque(maxlen=queue_size)

    def add(self, client: Client) -> None:
        with self._lock:
            self._queue.append(client)

    def pop(self) -> Optional[Client]:
        with self._lock:
            return self._queue.pop() if self._queue else None

    def is_full(self) -> bool:
        with self._lock:
            return self._queue.maxlen == len(self._queue)

    def __bool__(self) -> bool:
        with self._lock:
            return bool(self._queue)

    def __len__(self) -> int:
        return len(self._queue)


class ClientListener(metaclass=ABCMeta):
    @abstractmethod
    def on_arrived(self, client: Client) -> None:
        pass

    @abstractmethod
    def on_scheduled(self, client: Client) -> None:
        pass

    @abstractmethod
    def on_queued(self, client: Client) -> None:
        pass

    @abstractmethod
    def on_popped_from_queue(self, client: Client) -> None:
        pass

    @abstractmethod
    def on_processing_finished(self, client: Client) -> None:
        pass

    @abstractmethod
    def on_processing_started(self, client: Client) -> None:
        pass

    @abstractmethod
    def on_all_processed(self) -> None:
        pass
