import expr as ex
from error_handler import ErrorHandler
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
        self._cur = 0

    def expression(self) -> ex.Expr:
        return self.equality()

    def equality(self) -> ex.Expr:
        expr = self.comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            op = self._previous()
            right = self.comparison()
            expr = ex.Binary(expr, op, right)

        return expr

    def comparison(self) -> ex.Expr:
        expr = self.term()

        while self._match(
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            op = self._previous()
            right = self.term()
            expr = ex.Binary(expr, op, right)

        return expr

    def term(self) -> ex.Expr:
        expr = self.factor()

        while self._match(
            TokenType.PLUS,
            TokenType.MINUS,
        ):
            op = self._previous()
            right = self.factor()
            expr = ex.Binary(expr, op, right)

        return expr

    def factor(self) -> ex.Expr:
        expr = self.unary()

        while self._match(
            TokenType.STAR,
            TokenType.SLASH,
        ):
            op = self._previous()
            right = self.unary()
            expr = ex.Binary(expr, op, right)

        return expr

    def unary(self) -> ex.Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            op = self._previous()
            right = self.unary()
            return ex.Unary(op, right)

        return self.primary()

    def primary(self) -> ex.Expr:
        if self._match(
            TokenType.FALSE,
            TokenType.TRUE,
            TokenType.NIL,
            TokenType.STRING,
            TokenType.NUMBER,
        ):
            return ex.Literal(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return ex.Grouping(expr)

        raise self._error(self._peek(), "Expected expression")

    def _consume(self, type: TokenType, msg: str):
        if self._check(type):
            return self._advance()

        raise self._error(self._peek(), msg)

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._cur += 1
        return self._previous()

    def _previous(self) -> Token:
        return self.tokens[self._cur - 1]

    def _match(self, *types: TokenType) -> bool:
        for type in types:
            if self._check(type):
                self._advance()
                return True

        return False

    def _check(self, type: TokenType) -> bool:
        if self._is_at_end():
            return False

        return self._peek().type == type

    def _peek(self) -> Token:
        return self.tokens[self._cur]

    def _is_at_end(self) -> bool:
        return self._cur >= len(self.tokens)

    def _error(self, token: Token, msg: str):
        ErrorHandler.error(token, msg)
        return ParseError()
    
    # TODO: 6.3 Syntax Errors


class ParseError(RuntimeError):
    pass
