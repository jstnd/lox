import time
from typing import Any, Final, Optional

from .callable import LoxCallable, LoxClass, LoxInstance
from .environment import Environment
from .errors import LoxErrors, LoxRuntimeError
from .exceptions import LoxReturn
from .expr import Assign, Expr, Unary, Literal, Grouping, Binary, Variable, Logical, Call, Get, Set, This, Super
from .function import LoxFunction
from .stmt import Stmt, Print, Expression, Var, Block, If, While, Function, Return, Class
from .tokens import Token, TokenType
from .visitor import ExprVisitor, StmtVisitor


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.globals: Final = Environment()
        self._environment = self.globals

        self._locals: Final[dict[Expr, int]] = {}

        self.globals.define("clock", type("", (LoxCallable,), {
            "arity": lambda self: 0,
            "call": lambda self, interpreter, arguments: time.time(),
            "__str__": lambda self: "<native fn>"
        }))

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as e:
            LoxErrors.runtime_error(e)

    def resolve(self, expr: Expr, depth: int) -> None:
        self._locals[expr] = depth

    def visit_assign_expr(self, expr: Assign) -> Any:
        value: Any = self._evaluate(expr.value)

        distance: int = self._locals.get(expr)
        if distance is not None:
            self._environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

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

    def visit_call_expr(self, expr: Call) -> Any:
        callee: Any = self._evaluate(expr.callee)

        arguments: list[Any] = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        function: LoxCallable = callee
        if len(arguments) != function.arity():
            raise LoxRuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return function.call(self, arguments)

    def visit_get_expr(self, expr: Get) -> Any:
        obj: Any = self._evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return self._evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr.value

    def visit_logical_expr(self, expr: Logical) -> Any:
        left: Any = self._evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        return self._evaluate(expr.right)

    def visit_set_expr(self, expr: Set) -> Any:
        obj: Any = self._evaluate(expr.obj)

        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value: Any = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: Super) -> Any:
        distance: int = self._locals[expr]
        superclass: LoxClass = self._environment.get_at(distance, "super")
        obj: LoxInstance = self._environment.get_at(distance - 1, "this")

        method: LoxFunction = superclass.find_method(expr.method.lexeme)

        if method is None:
            raise LoxRuntimeError(expr.method, f"Undefined property '{expr.method.lexeme}'.")

        return method.bind(obj)

    def visit_this_expr(self, expr: This) -> Any:
        return self._look_up_variable(expr.keyword, expr)

    def visit_unary_expr(self, expr: Unary) -> Any:
        right: Any = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self._is_truthy(right)
            case TokenType.MINUS:
                self._check_number_operand(expr.operator, right)
                return -float(right)

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self._look_up_variable(expr.name, expr)

    def _look_up_variable(self, name: Token, expr: Expr) -> Any:
        distance: int = self._locals.get(expr)
        if distance is not None:
            return self._environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def visit_block_stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self._environment))

    def visit_class_stmt(self, stmt: Class) -> None:
        superclass: Optional[Any] = None
        if stmt.superclass is not None:
            superclass = self._evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise LoxRuntimeError(stmt.superclass.name, "Superclass must be a class.")

        self._environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self._environment = Environment(self._environment)
            self._environment.define("super", superclass)

        methods: dict[str, LoxFunction] = {}
        for method in stmt.methods:
            function = LoxFunction(method, self._environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function

        klass = LoxClass(stmt.name.lexeme, superclass, methods)

        if superclass is not None:
            self._environment = self._environment.enclosing

        self._environment.assign(stmt.name, klass)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        function = LoxFunction(stmt, self._environment, False)
        self._environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: If) -> None:
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        value: Any = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visit_return_stmt(self, stmt: Return) -> None:
        value: Any = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)

        raise LoxReturn(value)

    def visit_var_stmt(self, stmt: Var) -> None:
        value: Any = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

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

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous: Environment = self._environment

        try:
            self._environment = environment

            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = previous
