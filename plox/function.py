from __future__ import annotations
from typing import TYPE_CHECKING, Any, Final

from .callable import LoxCallable
from .environment import Environment
from .exceptions import LoxReturn

if TYPE_CHECKING:
    from .callable import LoxInstance
    from .interpreter import Interpreter
    from .stmt import Function


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool):
        self._declaration: Final = declaration
        self._closure: Final = closure
        self._is_initializer: Final = is_initializer

    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment = Environment(self._closure)
        environment.define("this", instance)
        return LoxFunction(self._declaration, environment, self._is_initializer)

    def arity(self) -> int:
        return len(self._declaration.params)

    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment: Environment = Environment(self._closure)

        for i in range(len(self._declaration.params)):
            environment.define(self._declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self._declaration.body, environment)
        except LoxReturn as r:
            if self._is_initializer:
                return self._closure.get_at(0, "this")

            return r.value

        if self._is_initializer:
            return self._closure.get_at(0, "this")

    def __str__(self):
        return f"<fn {self._declaration.name.lexeme}>"
