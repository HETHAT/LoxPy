from enum import Enum
from typing import TYPE_CHECKING

from lox_callable import LoxCallable
from lox_function import LoxFunction
from lox_instance import LoxInstance

if TYPE_CHECKING:
    import interpreter

ClassType = Enum("ClassType", "NONE, CLASS, SUBCLASS")


class LoxClass(LoxCallable):
    def __init__(
        self,
        name: str,
        superclass: "LoxClass | None",
        methods: dict[str, LoxFunction],
    ) -> None:
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is not None:
            return initializer.arity()
        return 0

    def call(
        self, interpreter: "interpreter.Interpreter", args: list
    ) -> object:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, args)
        return instance

    def find_method(self, name: str):
        method = self.methods.get(name)
        if method is not None:
            return method
        if self.superclass is not None:
            return self.superclass.find_method(name)

    def __str__(self) -> str:
        return f"<{self.name} class>"
