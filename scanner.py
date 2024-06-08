from error_handler import ErrorHandler
from token_ import Token
from token_type import TokenType


class Scanner:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.tokens: list[Token] = []

        self._cur = 0
        self._start = 0
        self._line = 1

        self.keywords = {
            "add": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }
        self.single_tokens = {
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            "-": TokenType.MINUS,
            "+": TokenType.PLUS,
            ";": TokenType.SEMICOLON,
            "*": TokenType.STAR,
        }

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self._start = self._cur
            self.scan_token()

        return self.tokens

    def scan_token(self):
        c = self._advance()

        if c in self.single_tokens:
            self.add_token(self.single_tokens[c])

        elif c == "!":
            if self._match("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG)

        elif c == "=":
            if self._match("="):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)

        elif c == "<":
            if self._match("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)

        elif c == ">":
            if self._match("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
            return

        elif c == "/":
            if self._match("/"):
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            else:
                self.add_token(TokenType.SLASH)

        elif c == "\n":
            self._line += 1

        elif c.isspace():
            pass

        elif c == '"':
            self._string()

        elif c.isdigit():
            self._number()

        elif c.isalpha():
            self._identifier()

        else:
            ErrorHandler.error(self._line, "Unexpected character.")

    def add_token(self, type: TokenType, literal=None):
        text = self.source[self._start : self._cur]
        self.tokens.append(Token(type, text, literal, self._line))

    def _string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self._line += 1
            self._advance()

        if self._is_at_end():
            ErrorHandler.error(self._line, "Unexpected character.")
            return

        self._advance()
        value = self.source[self._start + 1 : self._cur - 1]
        self.add_token(TokenType.STRING, value)

    def _number(self):
        while self._peek().isdigit():
            self._advance()

        if self._peek() == ".":
            self._advance()

            while self._peek().isdigit():
                self._advance()

        value = float(self.source[self._start : self._cur])
        self.add_token(TokenType.NUMBER, value)

    def _identifier(self):
        while self._peek().isalnum():
            self._advance()

        text = self.source[self._start : self._cur]
        self.add_token(self.keywords.get(text, TokenType.IDENTIFIER))

    def _advance(self):
        if self._is_at_end():
            return "\0"
        self._cur += 1
        return self.source[self._cur - 1]

    def _match(self, c: str):
        if self._peek() == c:
            self._cur += 1
            return True

        return False

    def _peek(self):
        if self._is_at_end():
            return "\0"
        return self.source[self._cur]

    def _peek_next(self):
        if self._cur + 1 >= len(self.source):
            return "\0"
        return self.source[self._cur + 1]

    def _is_at_end(self):
        return self._cur >= len(self.source)
