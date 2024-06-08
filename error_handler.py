import sys


class ErrorHandler:
    had_error: bool = False

    @classmethod
    def error(cls, line: int, msg: str) -> None:
        cls.report(line, "", msg)

    @classmethod
    def report(cls, line: int, where: str, msg: str) -> None:
        print(f"[Line {line}] Error {where}: {msg}", file=sys.stderr)
        cls.had_error = True
