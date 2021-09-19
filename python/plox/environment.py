from __future__ import annotations
from typing import TYPE_CHECKING, Any, Final

from .errors import LoxRuntimeError

if TYPE_CHECKING:
    from .tokens import Token


class Environment:
    def __init__(self, enclosing: Environment = None):
        self.enclosing: Final = enclosing
        self._values: Final[dict[str, Any]] = dict()

    def get(self, name: Token) -> Any:
        if name.lexeme in self._values.keys():
            return self._values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str) -> Any:
        return self.ancestor(distance)._values[name]

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self._values.keys():
            self._values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance)._values[name.lexeme] = value

    def define(self, name: str, value: Any) -> None:
        self._values[name] = value

    def ancestor(self, distance: int) -> Environment:
        environment: Environment = self
        for _ in range(distance):
            environment = environment.enclosing

        return environment
