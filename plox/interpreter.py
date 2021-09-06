from typing import Any

from .errors import LoxErrors, LoxRuntimeError
from .expr import Expr, Unary, Literal, Grouping, Binary
from .tokens import Token, TokenType
from .visitor import Visitor


class Interpreter(Visitor):
    def interpret(self, expression: Expr) -> None:
        try:
            value: Any = self._evaluate(expression)
            print(self._stringify(value))
        except LoxRuntimeError as e:
            LoxErrors.runtime_error(e)

    def visit_binary_expr(self, expr: Binary) -> Any:
        left: Any = self._evaluate(expr.left)
        right: Any = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.GREATER:
                self._check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self._check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.PLUS:
                if (type(left) is float and type(right) is float) or (type(left) is str and type(right) is str):
                    return left + right

                raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                return left / right
            case TokenType.STAR:
                self._check_number_operands(expr.operator, left, right)
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
                self._check_number_operand(expr.operator, right)
                return -float(right)

    def _check_number_operand(self, operator: Token, operand: Any) -> None:
        if type(operand) is float:
            return

        raise LoxRuntimeError(operator, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        if type(left) is float and type(right) is float:
            return

        raise LoxRuntimeError(operator, "Operands must be numbers.")

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

    def _stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"

        if type(obj) is float:
            text = str(obj)
            if text.endswith(".0"):
                text = text[0:len(text) - 2]

            return text

        return str(obj)

    def _evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)
