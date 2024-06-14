from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import interpreter


class Callable(ABC):
    @abstractmethod
    def arity(self) -> int:
        ...

    @abstractmethod
    def call(self, interpreter: "interpreter.Interpreter", args: list) -> object:
        ...
