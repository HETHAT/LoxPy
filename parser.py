import expr as ex
from error_handler import ErrorHandler, ParseErr
from token_ import Token
from token_type import TokenType

# expression     → equality ;
# equality       → comparison ( ( "!=" | "==" ) comparison )* ;
# comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
# term           → factor ( ( "-" | "+" ) factor )* ;
# factor         → unary ( ( "/" | "*" ) unary )* ;
# unary          → ( "!" | "-" ) unary
#                | primary ;
# primary        → NUMBER | STRING | "true" | "false" | "nil"
#                | "(" expression ")" ;


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.cur = 0

    def parse(self):
        try:
            return self.expression()
        except ParseErr:
            return None

    def expression(self) -> ex.Expr:
        return self.equality()

    def equality(self) -> ex.Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            op = self.previous()
            right = self.comparison()
            expr = ex.Binary(expr, op, right)

        return expr

    def comparison(self) -> ex.Expr:
        expr = self.term()

        while self.match(
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            op = self.previous()
            right = self.term()
            expr = ex.Binary(expr, op, right)

        return expr

    def term(self) -> ex.Expr:
        expr = self.factor()

        while self.match(
            TokenType.PLUS,
            TokenType.MINUS,
        ):
            op = self.previous()
            right = self.factor()
            expr = ex.Binary(expr, op, right)

        return expr

    def factor(self) -> ex.Expr:
        expr = self.unary()

        while self.match(
            TokenType.STAR,
            TokenType.SLASH,
        ):
            op = self.previous()
            right = self.unary()
            expr = ex.Binary(expr, op, right)

        return expr

    def unary(self) -> ex.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            op = self.previous()
            right = self.unary()
            return ex.Unary(op, right)

        return self.primary()

    def primary(self) -> ex.Expr:
        if self.match(
            TokenType.FALSE,
            TokenType.TRUE,
            TokenType.NIL,
            TokenType.STRING,
            TokenType.NUMBER,
        ):
            return ex.Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return ex.Grouping(expr)

        raise self.error(self.peek(), "Expected expression")

    def consume(self, type: TokenType, msg: str):
        if self.check(type):
            return self.advance()

        raise self.error(self.peek(), msg)

    def advance(self) -> Token:
        if not self.is_at_end():
            self.cur += 1
        return self.previous()

    def previous(self) -> Token:
        return self.tokens[self.cur - 1]

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False

        return self.peek().type == type

    def peek(self) -> Token:
        return self.tokens[self.cur]

    def is_at_end(self) -> bool:
        return self.cur >= len(self.tokens)

    def error(self, token: Token, msg: str):
        ErrorHandler.error(token, msg)
        return ParseErr()

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in (
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return

            self.advance()
