from __future__ import annotations
from typing import TYPE_CHECKING, Any, Final

from .callable import LoxCallable
from .environment import Environment
from .exceptions import LoxReturn

if TYPE_CHECKING:
    from .interpreter import Interpreter
    from .stmt import Function


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function):
        self._declaration: Final = declaration

    def arity(self) -> int:
        return len(self._declaration.params)

    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment: Environment = Environment(interpreter.globals)

        for i in range(len(self._declaration.params)):
            environment.define(self._declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self._declaration.body, environment)
        except LoxReturn as r:
            return r.value

        return None

    def __str__(self):
        return f"<fn {self._declaration.name.lexeme}>"
