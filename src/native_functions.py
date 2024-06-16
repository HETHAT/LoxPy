import time

from lox_callable import LoxCallable


class Clock(LoxCallable):
    def arity(self):
        return 0

    def call(self, interpreter, args):
        return time.time()

    def __str__(self) -> str:
        return "<native fn>"
