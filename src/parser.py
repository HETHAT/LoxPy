import expr as ex
import stmt as st
from error_handler import ErrorHandler, ParseErr
from token_ import Token
from token_type import TokenType


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.cur = 0

    def parse(self) -> list[st.Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseErr:
            self.synchronize()
            return None

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return st.Block(self.block())
        return self.expression_statement()

    def print_statement(self):
        val = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after value")
        return st.Print(val)

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(
            TokenType.SEMICOLON, "Expect ';' after variable declaration."
        )
        return st.Var(name, initializer)

    def expression_statement(self):
        val = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after expression")
        return st.Expression(val)

    def block(self):
        statements = []

        while not (self.check(TokenType.RIGHT_BRACE) or self.is_at_end()):
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression(self) -> ex.Expr:
        return self.assignment()

    def assignment(self):
        expr = self.logic_or()

        if self.match(TokenType.EQUAL):
            equal = self.previous()
            val = self.assignment()

            if isinstance(expr, ex.Variable):
                return ex.Assign(expr.name, val)

            self.error(equal, "Invalid assignment target.")

        return expr

    def logic_or(self):
        expr = self.logic_and()

        while self.match(TokenType.OR):
            op = self.previous()
            right = self.logic_and()
            expr = ex.Logical(expr, op, right)

        return expr

    def logic_and(self):
        expr = self.equality()

        while self.match(TokenType.OR):
            op = self.previous()
            right = self.equality()
            expr = ex.Logical(expr, op, right)

        return expr

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

        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return ex.Grouping(expr)

        elif self.match(TokenType.IDENTIFIER):
            return ex.Variable(self.previous())

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
        return self.peek().type == TokenType.EOF

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
