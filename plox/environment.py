from __future__ import annotations
from typing import TYPE_CHECKING, Any, Final

from .errors import LoxRuntimeError

if TYPE_CHECKING:
    from .tokens import Token


class Environment:
    def __init__(self):
        self._values: Final[dict[str, Any]] = dict()

    def get(self, name: Token) -> Any:
        if name.lexeme in self._values.keys():
            return self._values[name.lexeme]

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name: str, value: Any) -> None:
        self._values[name] = value
