from typing import Any

from .expr import Expr, Unary, Literal, Grouping, Binary
from .tokens import TokenType
from .visitor import Visitor


class Interpreter(Visitor):
    def visit_binary_expr(self, expr: Binary) -> Any:
        left: Any = self._evaluate(expr.left)
        right: Any = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.GREATER:
                return left > right
            case TokenType.GREATER_EQUAL:
                return left >= right
            case TokenType.LESS:
                return left < right
            case TokenType.LESS_EQUAL:
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)
            case TokenType.MINUS:
                return left - right
            case TokenType.PLUS:
                if type(left) == type(right):
                    return left + right
            case TokenType.SLASH:
                return left / right
            case TokenType.STAR:
                return left * right

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return self._evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr.value

    def visit_unary_expr(self, expr: Unary) -> Any:
        right: Any = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self._is_truthy(right)
            case TokenType.MINUS:
                return -float(right)

    def _is_truthy(self, obj: Any) -> bool:
        if obj is None:
            return False

        if type(obj) is bool:
            return obj

        return True

    def _is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True

        if a is None:
            return False
        
        return a == b

    def _evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)
