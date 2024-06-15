from error_handler import RuntimeErr
from token_ import Token


class Environment:
    def __init__(self, enclosing: "Environment | None" = None) -> None:
        self.enclosing: Environment | None = enclosing
        self.values: dict[str, object] = {}

    def define(self, name: str, val):
        self.values[name] = val

    def ancestor(self, distance: int):
        env = self
        for _ in range(distance):
            if env.enclosing is None:
                break
            env = env.enclosing
        return env

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeErr(f"Undefined variable '{name.lexeme}'.", token=name)

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)

    def assign(self, name: Token, val):
        if name.lexeme in self.values:
            self.values[name.lexeme] = val
            return

        if self.enclosing is not None:
            return self.enclosing.assign(name, val)

        raise RuntimeErr(f"Undefined variable '{name.lexeme}'.", token=name)

    def assign_at(self, distance: int, name: Token, val):
        self.ancestor(distance).values[name.lexeme] = val
