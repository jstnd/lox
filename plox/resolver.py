from __future__ import annotations
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Final, Union

from .errors import LoxErrors
from .visitor import ExprVisitor, StmtVisitor

if TYPE_CHECKING:
    from .expr import Assign, Binary, Call, Expr, Get, Grouping, Literal, Logical, Set, Unary, Variable
    from .interpreter import Interpreter
    from .stmt import Stmt, Block, Class, Expression, Function, If, Print, Return, Var, While
    from .tokens import Token


class _FunctionType(Enum):
    NONE = auto(),
    FUNCTION = auto(),
    METHOD = auto()


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter: Interpreter):
        self._interpreter: Final = interpreter
        self._scopes: Final[list[dict[str, bool]]] = []
        self._current_function: _FunctionType = _FunctionType.NONE

    def resolve_statements(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self._resolve(statement)

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self.resolve_statements(stmt.statements)
        self._end_scope()

    def visit_class_stmt(self, stmt: Class) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)

        for method in stmt.methods:
            declaration = _FunctionType.METHOD
            self._resolve_function(method, declaration)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._resolve(stmt.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, _FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: If) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self._resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        if self._current_function == _FunctionType.NONE:
            LoxErrors.token_error(stmt.keyword, "Can't return from top-level code.")

        if stmt.value is not None:
            self._resolve(stmt.value)

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self._define(stmt.name)

    def visit_while_stmt(self, stmt: While) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_assign_expr(self, expr: Assign) -> Any:
        self._resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: Binary) -> Any:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_call_expr(self, expr: Call) -> Any:
        self._resolve(expr.callee)

        for argument in expr.arguments:
            self._resolve(argument)

    def visit_get_expr(self, expr: Get) -> Any:
        self._resolve(expr.obj)

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        self._resolve(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return None

    def visit_logical_expr(self, expr: Logical) -> Any:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_set_expr(self, expr: Set) -> Any:
        self._resolve(expr.value)
        self._resolve(expr.obj)

    def visit_unary_expr(self, expr: Unary) -> Any:
        self._resolve(expr.right)

    def visit_variable_expr(self, expr: Variable) -> Any:
        if len(self._scopes) != 0 and self._scopes[-1].get(expr.name.lexeme) is False:
            LoxErrors.token_error(expr.name, "Can't read local variable in its own initializer.")

        self._resolve_local(expr, expr.name)

    def _resolve(self, es: Union[Expr, Stmt]) -> None:
        es.accept(self)

    def _resolve_function(self, function: Function, type: _FunctionType) -> None:
        enclosing_function: _FunctionType = self._current_function
        self._current_function = type

        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)

        self.resolve_statements(function.body)
        self._end_scope()

        self._current_function = enclosing_function

    def _resolve_local(self, expr: Expr, name: Token) -> None:
        for i in range(len(self._scopes) - 1, -1, -1):
            if name.lexeme in self._scopes[i].keys():
                self._interpreter.resolve(expr, len(self._scopes) - 1 - i)
                return

    def _begin_scope(self) -> None:
        self._scopes.append({})

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        if len(self._scopes) == 0:
            return

        if name.lexeme in self._scopes[-1].keys():
            LoxErrors.token_error(name, "Already a variable with this name in this scope.")

        self._scopes[-1][name.lexeme] = False

    def _define(self, name: Token) -> None:
        if len(self._scopes) == 0:
            return

        self._scopes[-1][name.lexeme] = True
