import pathlib
import sys
from parser import Parser

from error_handler import ErrorHandler
from interpreter import Interpreter
from scanner import Scanner

interpreter = Interpreter()


def run(content: str) -> None:
    scanner = Scanner(content)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    expression = parser.parse()

    # Stop if there was a syntax error.
    if ErrorHandler.had_error:
        return

    interpreter.interpret(expression)  # pyright: ignore


def run_file(path: pathlib.Path) -> None:
    with path.open(mode="r") as f:
        run(f.read())

    if ErrorHandler.had_error:
        exit(65)

    if ErrorHandler.had_runtime_error:
        exit(70)


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
