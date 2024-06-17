from typing import TYPE_CHECKING

import expr as ex
import stmt as st
from error_handler import ErrorHandler
from lox_class import ClassType
from lox_function import FunctionType

if TYPE_CHECKING:
    import interpreter
    from token_ import Token


class Resolver(ex.Visitor, st.Visitor):
    def __init__(self, interpreter: "interpreter.Interpreter") -> None:
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve_expr(self, expr: ex.Expr):
        return expr.accept(self)

    def resolve_function(self, stmt: st.Function, type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in stmt.params:
            self.declare(param)
            self.define(param)
        self.resolve_stmts(stmt.body)
        self.end_scope()
        self.current_function = enclosing_function

    def resolve_local(self, expr: ex.Expr, name: "Token"):
        for i in range(len(self.scopes)):
            if name.lexeme in self.scopes[~i]:
                self.interpreter.resolve(expr, i)
                return

    def resolve_stmt(self, stmt: st.Stmt):
        stmt.accept(self)

    def resolve_stmts(self, stmts: list[st.Stmt]):
        for stmt in stmts:
            self.resolve_stmt(stmt)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: "Token"):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            ErrorHandler.error(
                name, "Already a variable with this name in this scope."
            )

        scope[name.lexeme] = False

    def define(self, name: "Token"):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def visit_block_stmt(self, stmt: st.Block):
        self.begin_scope()
        self.resolve_stmts(stmt.statements)
        self.end_scope()

    def visit_class_stmt(self, stmt: st.Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None:
            if stmt.superclass.name.lexeme == stmt.name.lexeme:
                ErrorHandler.error(
                    stmt.superclass.name, "A class can't inherit from itself."
                )
            self.current_class = ClassType.SUBCLASS
            self.resolve_expr(stmt.superclass)
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            type = FunctionType.METHOD
            if method.name.lexeme == "init":
                type = FunctionType.INITIALIZER

            self.resolve_function(method, type)

        self.end_scope()
        if stmt.superclass is not None:
            self.end_scope()
        self.current_class = enclosing_class

    def visit_expression_stmt(self, stmt: st.Expression):
        self.resolve_expr(stmt.expression)

    def visit_function_stmt(self, stmt: st.Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: st.If):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt: st.Print):
        self.resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt: st.Return):
        if self.current_function == FunctionType.NONE:
            ErrorHandler.error(
                stmt.keyword, "Can't return from top-level code."
            )

        if (
            self.current_function == FunctionType.INITIALIZER
            and stmt.val is not None
        ):
            ErrorHandler.error(
                stmt.keyword, "Can't return a value from an initializer."
            )

        if stmt.val is not None:
            self.resolve_expr(stmt.val)

    def visit_var_stmt(self, stmt: st.Var):
        self.declare(stmt.name)

        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)

        self.define(stmt.name)

    def visit_while_stmt(self, stmt: st.While):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    def visit_assign_expr(self, expr: ex.Assign):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: ex.Binary):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_call_expr(self, expr: ex.Call):
        self.resolve_expr(expr.callee)
        for arg in expr.args:
            self.resolve_expr(arg)

    def visit_get_expr(self, expr: ex.Get):
        self.resolve_expr(expr.obj)

    def visit_grouping_expr(self, expr: ex.Grouping):
        self.resolve_expr(expr.expression)

    def visit_literal_expr(self, expr: ex.Literal):
        pass

    def visit_logical_expr(self, expr: ex.Logical):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_set_expr(self, expr: ex.Set):
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.obj)

    def visit_super_expr(self, expr: ex.Super):
        if self.current_class == ClassType.NONE:
            ErrorHandler.error(
                expr.keyword, "Can't use 'super' outside of a class."
            )
        if self.current_class == ClassType.CLASS:
            ErrorHandler.error(
                expr.keyword, "Can't use 'super' in a class with no superclass."
            )
        self.resolve_local(expr, expr.keyword)

    def visit_this_expr(self, expr: ex.This):
        if self.current_class == ClassType.NONE:
            ErrorHandler.error(
                expr.keyword, "Can't use 'this' outside of a class."
            )
            return

        self.resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr: ex.Unary):
        self.resolve_expr(expr.right)

    def visit_variable_expr(self, expr: ex.Variable):
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
            ErrorHandler.error(
                expr.name, "Can't read local variable in its own initializer."
            )

        self.resolve_local(expr, expr.name)
