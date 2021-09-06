from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from .ast_printer import AstPrinter
from .errors import LoxErrors
from .parser import Parser
from .scanner import Scanner

if TYPE_CHECKING:
    from .expr import Expr
    from .tokens import Token


class Lox:
    def run(self, pgm: str):
        scanner = Scanner(pgm)
        tokens: list[Token] = scanner.scan_tokens()
        parser = Parser(tokens)
        expression: Expr = parser.parse()

        if LoxErrors.had_error:
            return

        print(AstPrinter().print(expression))

    def run_prompt(self):
        while True:
            line = input("> ")
            if not line:
                break
            self.run(line)
            LoxErrors.had_error = False


# if __name__ == "__main__":
#     lox = Lox()
#
#     if len(sys.argv) > 2:
#         print("Usage: lox.py [script]")
#         sys.exit(64)
#     elif len(sys.argv) == 2:
#         lox.run(open(sys.argv[1]).read())
#         if LoxErrors.had_error:
#             sys.exit(65)
#     else:
#         lox.run_prompt()
