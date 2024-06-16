from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from token_ import Token

V = TypeVar("V")


class Visitor(ABC, Generic[V]):
    @abstractmethod
    def visit_assign_expr(self, expr: "Assign") -> V:
        ...

    @abstractmethod
    def visit_binary_expr(self, expr: "Binary") -> V:
        ...

    @abstractmethod
    def visit_call_expr(self, expr: "Call") -> V:
        ...

    @abstractmethod
    def visit_get_expr(self, expr: "Get") -> V:
        ...

    @abstractmethod
    def visit_grouping_expr(self, expr: "Grouping") -> V:
        ...

    @abstractmethod
    def visit_literal_expr(self, expr: "Literal") -> V:
        ...

    @abstractmethod
    def visit_logical_expr(self, expr: "Logical") -> V:
        ...

    @abstractmethod
    def visit_set_expr(self, expr: "Set") -> V:
        ...

    @abstractmethod
    def visit_this_expr(self, expr: "This") -> V:
        ...

    @abstractmethod
    def visit_unary_expr(self, expr: "Unary") -> V:
        ...

    @abstractmethod
    def visit_variable_expr(self, expr: "Variable") -> V:
        ...


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[V]) -> V:
        ...


class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name: Token = name
        self.value: Expr = value

    def accept(self, visitor: Visitor):
        return visitor.visit_assign_expr(self)


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: Visitor):
        return visitor.visit_binary_expr(self)


class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, args: list[Expr]):
        self.callee: Expr = callee
        self.paren: Token = paren
        self.args: list[Expr] = args

    def accept(self, visitor: Visitor):
        return visitor.visit_call_expr(self)


class Get(Expr):
    def __init__(self, obj: Expr, name: Token):
        self.obj: Expr = obj
        self.name: Token = name

    def accept(self, visitor: Visitor):
        return visitor.visit_get_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    def accept(self, visitor: Visitor):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visit_literal_expr(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: Visitor):
        return visitor.visit_logical_expr(self)


class Set(Expr):
    def __init__(self, obj: Expr, name: Token, value: Expr):
        self.obj: Expr = obj
        self.name: Token = name
        self.value: Expr = value

    def accept(self, visitor: Visitor):
        return visitor.visit_set_expr(self)


class This(Expr):
    def __init__(self, keyword: Token):
        self.keyword: Token = keyword

    def accept(self, visitor: Visitor):
        return visitor.visit_this_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator: Token = operator
        self.right: Expr = right

    def accept(self, visitor: Visitor):
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name: Token):
        self.name: Token = name

    def accept(self, visitor: Visitor):
        return visitor.visit_variable_expr(self)
