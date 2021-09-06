from __future__ import annotations

from typing import TYPE_CHECKING

from .tokens import TokenType

if TYPE_CHECKING:
    from .tokens import Token


class LoxErrors:
    had_error = False

    @staticmethod
    def error(line: int, message: str):
        LoxErrors.report(line, "", message)

    @staticmethod
    def token_error(token: Token, message: str):
        if token.type == TokenType.EOF:
            LoxErrors.report(token.line, " at end", message)
        else:
            LoxErrors.report(token.line, f" at '{token.lexeme}'", message)

    @staticmethod
    def report(line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        LoxErrors.had_error = True


class ParseError(Exception):
    pass
