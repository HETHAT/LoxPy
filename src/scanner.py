from error_handler import ErrorHandler
from token_ import Token
from token_type import TokenType


class Scanner:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.tokens: list[Token] = []

        self.cur = 0
        self.start = 0
        self.line = 1

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
            "%": TokenType.MOD,
        }

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.cur
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()

        if c in self.single_tokens:
            self.add_token(self.single_tokens[c])

        elif c == "!":
            if self.match("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG)

        elif c == "=":
            if self.match("="):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)

        elif c == "<":
            if self.match("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)

        elif c == ">":
            if self.match("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
            return

        elif c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)

        elif c == "\n":
            self.line += 1

        elif c.isspace():
            pass

        elif c == '"':
            self.string()

        elif c.isdigit():
            self.number()

        elif c.isalpha():
            self.identifier()

        else:
            ErrorHandler.error(self.line, "Unexpected character.")

    def add_token(self, type: TokenType, literal=None):
        text = self.source[self.start : self.cur]
        self.tokens.append(Token(type, text, literal, self.line))

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            ErrorHandler.error(self.line, "Unexpected character.")
            return

        self.advance()
        value = self.source[self.start + 1 : self.cur - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == ".":
            self.advance()

            while self.peek().isdigit():
                self.advance()

        value = float(self.source[self.start : self.cur])
        self.add_token(TokenType.NUMBER, value)

    def identifier(self):
        while self.peek().isalnum():
            self.advance()

        text = self.source[self.start : self.cur]
        type = self.keywords.get(text, TokenType.IDENTIFIER)
        literal = {"true": True, "false": False, "nil": None}.get(text)
        self.add_token(type, literal)

    def advance(self):
        if self.is_at_end():
            return "\0"
        self.cur += 1
        return self.source[self.cur - 1]

    def match(self, c: str):
        if self.peek() == c:
            self.cur += 1
            return True

        return False

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.cur]

    def peek_next(self):
        if self.cur + 1 >= len(self.source):
            return "\0"
        return self.source[self.cur + 1]

    def is_at_end(self):
        return self.cur >= len(self.source)
