from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from token_ import Token

V = TypeVar("V")


class Visitor(ABC, Generic[V]):
    @abstractmethod
    def visit_binary_expr(self, expr: "Binary") -> V:
        ...

    @abstractmethod
    def visit_unary_expr(self, expr: "Unary") -> V:
        ...

    @abstractmethod
    def visit_grouping_expr(self, expr: "Grouping") -> V:
        ...

    @abstractmethod
    def visit_literal_expr(self, expr: "Literal") -> V:
        ...


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[V]) -> V:
        ...


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor):
        return visitor.visit_binary_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor):
        return visitor.visit_unary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visit_literal_expr(self)
