from enum import Enum
from typing import TYPE_CHECKING

from lox_callable import LoxCallable
from lox_function import LoxFunction
from lox_instance import LoxInstance

if TYPE_CHECKING:
    import interpreter

ClassType = Enum("ClassType", "CLASS, NONE")


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict[str, LoxFunction]) -> None:
        self.name = name
        self.methods = methods

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is not None:
            return initializer.arity()
        return 0

    def call(self, interpreter: "interpreter.Interpreter", args: list) -> object:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, args)

    def find_method(self, name: str):
        return self.methods.get(name)

    def __str__(self) -> str:
        return f"<{self.name} class>"
