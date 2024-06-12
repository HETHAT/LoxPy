from error_handler import RuntimeErr
from token_ import Token


class Environment:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def define(self, name: str, val):
        self.values[name] = val

    def get(self, name: Token):  # name is
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        raise RuntimeErr(f"Undefined variable '{name.lexeme}'.", token=name)

    def assign(self, name: Token, val):
        if name.lexeme in self.values:
            self.values[name.lexeme] = val
            return

        raise RuntimeErr(f"Undefined variable '{name.lexeme}'.", token=name)
