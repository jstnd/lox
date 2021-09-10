from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .errors import LoxErrors
from .interpreter import Interpreter
from .parser import Parser
from .resolver import Resolver
from .scanner import Scanner

if TYPE_CHECKING:
    from .stmt import Stmt
    from .tokens import Token


class Lox:
    interpreter: Final = Interpreter()

    def run(self, pgm: str):
        scanner = Scanner(pgm)
        tokens: list[Token] = scanner.scan_tokens()
        parser = Parser(tokens)
        statements: list[Stmt] = parser.parse()

        if LoxErrors.had_error:
            return

        resolver = Resolver(Lox.interpreter)
        resolver.resolve_statements(statements)

        if LoxErrors.had_error:
            return

        Lox.interpreter.interpret(statements)

    def run_prompt(self):
        while True:
            line = input("> ")
            if not line:
                break
            self.run(line)
            LoxErrors.had_error = False
