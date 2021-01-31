from abc import ABCMeta, abstractmethod
from uuid import uuid1


class Runnable(metaclass=ABCMeta):
    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


class Printable:
    def _print(self, msg: str, *args, **kwargs) -> None:
        print(f'{self}: {msg}', *args, **kwargs)

    @classmethod
    def __str__(cls) -> str:
        return cls.__name__


class Identifiable:
    def __init__(self):
        self._id = uuid1().int

    @property
    def id(self) -> int:
        return self._id

    def __str__(self) -> str:
        return f'{self.__class__.__name__} (id={self._id})'
