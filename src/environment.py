from error_handler import RuntimeErr
from token_ import Token


class Environment:
    def __init__(self, enclosing: "Environment | None" = None) -> None:
        self.enclosing: Environment | None = enclosing
        self.values: dict[str, object] = {}

    def define(self, name: str, val):
        self.values[name] = val

    def get(self, name: Token):  # name is
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeErr(f"Undefined variable '{name.lexeme}'.", token=name)

    def assign(self, name: Token, val):
        if name.lexeme in self.values:
            self.values[name.lexeme] = val
            return

        if self.enclosing is not None:
            return self.enclosing.assign(name, val)

        raise RuntimeErr(f"Undefined variable '{name.lexeme}'.", token=name)
