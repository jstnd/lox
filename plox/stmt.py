from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .expr import Expr
    from .visitor import StmtVisitor


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> Any:
        pass


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_expression_stmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_print_stmt(self)
