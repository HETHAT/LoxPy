import expr as ex
import native_functions
import stmt as st
from environment import Environment
from error_handler import ErrorHandler, Return, RuntimeErr
from lox_class import LoxClass
from lox_function import LoxFunction
from lox_instance import LoxInstance
from token_type import TokenType


class Interpreter(ex.Visitor, st.Visitor):
    globals_ = Environment()

    def __init__(self) -> None:
        self.env = self.globals_
        self.globals_.define("clock", native_functions.Clock())
        self.locals = {}

    def interpret(self, statements: list[st.Stmt]):
        try:
            for stmt in statements:
                self.execute(stmt)
        except RuntimeErr as error:
            ErrorHandler.runtime_error(error)

    def evaluate(self, expr: ex.Expr):
        return expr.accept(self)

    def execute(self, stmt: st.Stmt):
        stmt.accept(self)

    def resolve(self, expr: ex.Expr, depth: int):
        self.locals[expr] = depth

    def execute_block(self, statements, environment):
        previous = self.env
        try:
            self.env = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.env = previous

    def visit_block_stmt(self, stmt: st.Block):
        self.execute_block(stmt.statements, Environment(self.env))
        return None

    def visit_class_stmt(self, stmt: st.Class):
        self.env.define(stmt.name.lexeme, None)
        methods = {}
        for method in stmt.methods:
            name = method.name.lexeme
            methods[name] = LoxFunction(method, self.env, name == "init")

        klass = LoxClass(stmt.name.lexeme, methods)
        self.env.assign(stmt.name, klass)
        return None

    def visit_expression_stmt(self, stmt: st.Expression):
        self.evaluate(stmt.expression)
        return None

    def visit_function_stmt(self, stmt: st.Function):
        func = LoxFunction(stmt, self.env)
        self.env.define(stmt.name.lexeme, func)
        return None

    def visit_if_stmt(self, stmt: st.If):
        condition = self.evaluate(stmt.condition)

        if self.truthy(condition):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: st.Print):
        print(self.stringfy(self.evaluate(stmt.expression)))
        return None

    def visit_return_stmt(self, stmt: st.Return):
        val = None
        if stmt.val is not None:
            val = self.evaluate(stmt.val)

        raise Return(val)

    def visit_var_stmt(self, stmt: st.Var):
        val = None
        if stmt.initializer is not None:
            val = self.evaluate(stmt.initializer)

        self.env.define(stmt.name.lexeme, val)
        return None

    def visit_while_stmt(self, stmt: st.While):
        while self.truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def visit_assign_expr(self, expr: ex.Assign):
        val = self.evaluate(expr.value)
        distance = self.locals.get(expr)
        if distance is not None:
            self.env.assign_at(distance, expr.name, val)
        else:
            self.globals_.assign(expr.name, val)

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

    def visit_call_expr(self, expr: ex.Call):
        callee = self.evaluate(expr.callee)
        args = [self.evaluate(arg) for arg in expr.args]
        if len(args) != callee.arity():
            raise RuntimeErr(
                f"Expected {callee.arity()} arguments got {len(args)}.", token=expr.paren
            )
        return callee.call(self, args)

    def visit_get_expr(self, expr: ex.Get):
        obj = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise RuntimeErr("Only instances have properties.", token=expr.name)

    def visit_grouping_expr(self, expr: ex.Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: ex.Literal):
        return expr.value

    def visit_set_expr(self, expr: ex.Set):
        obj = self.evaluate(expr.obj)

        if not isinstance(obj, LoxInstance):
            raise RuntimeErr("Only instances have properties.", token=expr.name)

        val = self.evaluate(expr.value)
        obj.set(expr.name, val)
        return val

    def visit_this_expr(self, expr: ex.This):
        return self.lookup_variable(expr.keyword, expr)

    def visit_logical_expr(self, expr: ex.Logical):
        left = self.evaluate(expr.left)

        if (expr.operator.type == TokenType.AND) ^ self.truthy(left):
            return left

        return self.evaluate(expr.right)

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
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name, expr: ex.Expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.env.get_at(distance, name.lexeme)
        else:
            return self.globals_.get(name)

    @staticmethod
    def truthy(val):
        return val is not None and val is not False

    @staticmethod
    def stringfy(val):
        if val is None:
            return "nil"
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(val)

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
        raise RuntimeErr("Operands must be two numbers or two strings.", token=operator)
