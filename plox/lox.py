import sys

from errors import LoxErrors
from scanner import Scanner


class Lox:
    def run(self, pgm: str):
        scanner = Scanner(pgm)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)

    def run_prompt(self):
        while True:
            line = input("> ")
            if not line:
                break
            self.run(line)
            LoxErrors.had_error = False


if __name__ == "__main__":
    lox = Lox()

    if len(sys.argv) > 1:
        print("Usage: plox [script]")
        sys.exit(64)
    elif len(sys.argv) == 1:
        lox.run(open(sys.argv[1]).read())
        if LoxErrors.had_error:
            sys.exit(65)
    else:
        lox.run_prompt()
