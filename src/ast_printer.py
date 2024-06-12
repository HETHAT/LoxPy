import expr as ex


class AstPrinter(ex.Visitor[str]):
    def print(self, expr: ex.Expr):
        return expr.accept(self)

    def parenthesize(self, name: str, *exprs: ex.Expr):
        builder = "(" + name
        for expr in exprs:
            builder += " " + expr.accept(self)
        builder += ")"
        return builder

    def visit_binary_expr(self, expr: ex.Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: ex.Grouping):
        return self.parenthesize("group", expr.expression)

    def visit_unary_expr(self, expr: ex.Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_literal_expr(self, expr: ex.Literal):
        return self.parenthesize(str(expr.value))


if __name__ == "__main__":
    from token_ import Token
    from token_type import TokenType

    expression = ex.Binary(
        ex.Unary(Token(TokenType.MINUS, "-", None, 1), ex.Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        ex.Grouping(ex.Literal(456)),
    )

    print(AstPrinter().print(expression))  # pyright: ignore
