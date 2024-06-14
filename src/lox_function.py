from typing import TYPE_CHECKING

from environment import Environment
from error_handler import Return
from lox_callable import Callable

if TYPE_CHECKING:
    import interpreter
    import stmt


class LoxFunction(Callable):
    def __init__(self, declaration: "stmt.Function", closure: Environment) -> None:
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "interpreter.Interpreter", args: list) -> object:
        env = Environment(self.closure)
        for param, arg in zip(self.declaration.params, args):
            env.define(param.lexeme, arg)
        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as e:
            return e.val

        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
