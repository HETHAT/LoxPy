import time

from lox_callable import LoxCallable

built_ins = {}


def define(cls):
    built_ins[cls.__name__.lower()] = cls()
    return cls


@define
class Clock(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter, args):
        return time.time()

    def __str__(self) -> str:
        return "<native clock fn>"


@define
class Input(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter, args):
        return input()

    def __str__(self) -> str:
        return "<native input fn>"


@define
class Length(LoxCallable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter, args):
        if not isinstance(args[0], str):
            raise Exception("Expect string argument.")
        return len(args[0])

    def __str__(self) -> str:
        return "<native length fn>"
