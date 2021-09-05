from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .tokens import Token
    from .visitor import Visitor


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        pass


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_binary_expr(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_grouping_expr(self)


@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_literal_expr(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_unary_expr(self)
