from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .expr import Assign, Binary, Call, Get, Grouping, Literal, Logical, Set, Super, This, Unary, Variable
    from .stmt import Block, Class, Expression, Function, If, Print, Return, Var, While


class ExprVisitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_call_expr(self, expr: Call) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_get_expr(self, expr: Get) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_logical_expr(self, expr: Logical) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_set_expr(self, expr: Set) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_super_expr(self, expr: Super) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_this_expr(self, expr: This) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> Any:
        raise NotImplementedError

    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> Any:
        raise NotImplementedError


class StmtVisitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt: Block) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_class_stmt(self, stmt: Class) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_function_stmt(self, stmt: Function) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_if_stmt(self, stmt: If) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_return_stmt(self, stmt: Return) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_while_stmt(self, stmt: While) -> None:
        raise NotImplementedError
