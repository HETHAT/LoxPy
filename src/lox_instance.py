from error_handler import RuntimeErr
from token_ import Token


class LoxInstance:
    def __init__(self, klass) -> None:
        self.klass = klass
        self.fields: dict[str, object] = {}

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeErr(f"Undefined property '{name.lexeme}'.", token=name)

    def set(self, name: Token, val):
        self.fields[name.lexeme] = val

    def __str__(self):
        return f"<{self.klass.name} instance>"
