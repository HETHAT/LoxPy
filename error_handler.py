import sys

from token_ import Token
from token_type import TokenType


class ErrorHandler:
    had_error: bool = False

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
