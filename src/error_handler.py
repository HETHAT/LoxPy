import sys

from token_ import Token
from token_type import TokenType


class ErrorHandler:
    had_error: bool = False
    had_runtime_error: bool = False

    @classmethod
    def runtime_error(cls, error: "RuntimeErr"):
        print(error.args[0] + f"\n[line {error.token.line}]")
        cls.had_runtime_error = True

    @classmethod
    def error(cls, where: int | Token, msg: str) -> None:
        if isinstance(where, Token):
            if where.type == TokenType.EOF:
                cls.report(where.line, " at end", msg)
            else:
                cls.report(where.line, f" at '{where.lexeme}'", msg)
        else:
            cls.report(where, "", msg)

    @classmethod
    def report(cls, line: int, where: str, msg: str) -> None:
        print(f"[Line {line}] Error {where}: {msg}", file=sys.stderr)
        cls.had_error = True


class ParseErr(RuntimeError):
    pass


class RuntimeErr(RuntimeError):
    def __init__(self, *args: object, token) -> None:
        super().__init__(*args)
        self.token = token
