from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .expr import Expr
    from .tokens import Token
    from .visitor import StmtVisitor


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> Any:
        pass


@dataclass
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_block_stmt(self)


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_expression_stmt(self)


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_if_stmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_print_stmt(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_var_stmt(self)
