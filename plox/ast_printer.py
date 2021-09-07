from __future__ import annotations
from typing import TYPE_CHECKING

from .visitor import ExprVisitor

if TYPE_CHECKING:
    from .expr import Expr, Unary, Literal, Grouping, Binary


class AstPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self._parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        return f"({name} {' '.join([e.accept(self) for e in exprs])})"
