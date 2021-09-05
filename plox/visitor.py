from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .expr import Binary, Grouping, Literal, Unary


class Visitor(ABC):
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
