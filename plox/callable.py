from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Final

from .errors import LoxRuntimeError

if TYPE_CHECKING:
    from .interpreter import Interpreter
    from .tokens import Token


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        raise NotImplementedError


class LoxClass(LoxCallable):
    def __init__(self, name: str):
        self.name: Final = name

    def arity(self) -> int:
        return 0

    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        return LoxInstance(self)

    def __str__(self):
        return self.name


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self._klass = klass
        self._fields: Final[dict[str, Any]] = {}

    def get(self, name: Token) -> Any:
        if name.lexeme in self._fields.keys():
            return self._fields[name.lexeme]

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self._fields[name.lexeme] = value

    def __str__(self):
        return f"{self._klass.name} instance"
