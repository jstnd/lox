from __future__ import annotations

from typing import TYPE_CHECKING

from .tokens import TokenType

if TYPE_CHECKING:
    from .tokens import Token


class LoxErrors:
    had_error = False
    had_runtime_error = False

    @staticmethod
    def error(line: int, message: str) -> None:
        LoxErrors.report(line, "", message)

    @staticmethod
    def runtime_error(error: LoxRuntimeError) -> None:
        print(f"{error.message}\n[line {error.token.line}]")
        LoxErrors.had_runtime_error = True

    @staticmethod
    def token_error(token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            LoxErrors.report(token.line, " at end", message)
        else:
            LoxErrors.report(token.line, f" at '{token.lexeme}'", message)

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")
        LoxErrors.had_error = True


class ParseError(Exception):
    pass


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super.__init__(self.message)

