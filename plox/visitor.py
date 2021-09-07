from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .expr import Binary, Grouping, Literal, Unary
    from .stmt import Expression, Print


class ExprVisitor(ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> Any:
        raise NotImplementedError


class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> None:
        raise NotImplementedError
