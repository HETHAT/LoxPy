import expr as ex
import stmt as st
from environment import Environment
from error_handler import ErrorHandler, RuntimeErr
from token_type import TokenType


class Interpreter(ex.Visitor, st.Visitor):
    def __init__(self) -> None:
        self.env = Environment()

    def interpret(self, statements: list[st.Stmt]):
        try:
            for stmt in statements:
                self.execute(stmt)
        except RuntimeErr as error:
            ErrorHandler.runtime_error(error)

    def execute(self, stmt: st.Stmt):
        stmt.accept(self)

    def evaluate(self, expr: ex.Expr):
        return expr.accept(self)

    def visit_expression_stmt(self, stmt: st.Expression):
        self.evaluate(stmt.expression)
        return None

    def visit_print_stmt(self, stmt: st.Print):
        print(self.stringfy(self.evaluate(stmt.expression)))
        return None

    def visit_var_stmt(self, stmt: st.Var):
        val = None
        if stmt.initializer is not None:
            val = self.evaluate(stmt.initializer)

        self.env.define(stmt.name.lexeme, val)
        return None

    def visit_assign_expr(self, expr: ex.Assign):
        val = self.evaluate(expr.value)
        self.env.assign(expr.name, val)
        return val

    def visit_binary_expr(self, expr: ex.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.PLUS:
                self.check_numstr_ops(TokenType.PLUS, left, right)
                return left + right
            case TokenType.MINUS:
                self.check_number_ops(TokenType.MINUS, left, right)
                return left - right
            case TokenType.STAR:
                self.check_number_ops(TokenType.STAR, left, right)
                return left * right
            case TokenType.SLASH:
                self.check_number_ops(TokenType.SLASH, left, right)
                return left / right
            case TokenType.GREATER:
                self.check_number_ops(TokenType.GREATER, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_ops(TokenType.GREATER_EQUAL, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_ops(TokenType.LESS, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_ops(TokenType.LESS_EQUAL, left, right)
                return left <= right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.BANG_EQUAL:
                return left != right

        return None  # Unreachable

    def visit_grouping_expr(self, expr: ex.Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: ex.Literal):
        return expr.value

    def visit_unary_expr(self, expr: ex.Unary):
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                self.check_number_op(TokenType.MINUS, right)
                return -right
            case TokenType.BANG:
                return not self.truthy(right)

        return None  # Unreachable

    def visit_variable_expr(self, expr: ex.Variable):
        return self.env.get(expr.name)

    @staticmethod
    def truthy(val):
        return val is not None and val is not False

    @staticmethod
    def stringfy(val):
        return "nil" if val is None else str(val)

    @staticmethod
    def check_number_op(operator, operand):
        if isinstance(operand, float):
            return
        raise RuntimeErr("Operand must be a number.", token=operator)

    @staticmethod
    def check_number_ops(operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeErr("Operands must be numbers.", token=operator)

    @staticmethod
    def check_numstr_ops(operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        if isinstance(left, str) and isinstance(right, str):
            return
        raise RuntimeErr(
            "Operands must be two numbers or two strings.", token=operator
        )
