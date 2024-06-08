import pathlib
import sys

from error_handler import ErrorHandler
from scanner import Scanner


def run(content: str) -> None:
    scanner = Scanner(content)
    tokens = scanner.scan_tokens()

    for token in tokens:
        print(token)


def run_file(path: pathlib.Path) -> None:
    with path.open(mode="r") as f:
        run(f.read())

    if ErrorHandler.had_error:
        exit(65)


def run_prompt() -> None:
    while line := input("> "):
        run(line)
        ErrorHandler.had_error = False


def main(args: list[str]) -> None:
    if len(args) > 1:
        print("Too many arguments")
        exit(64)

    elif len(args) == 1:
        run_file(pathlib.Path(args[0]))

    else:
        run_prompt()


if __name__ == "__main__":
    main(sys.argv[1:])
