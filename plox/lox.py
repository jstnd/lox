import sys

from scanner import Scanner


class Lox:
    def __init__(self):
        self.had_error = False

    def run(self, pgm: str):
        scanner = Scanner(pgm, self)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)

    def run_prompt(self):
        while True:
            line = input("> ")
            if not line:
                break
            self.run(line)
            self.had_error = False

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True


if __name__ == "__main__":
    lox = Lox()

    if len(sys.argv) > 1:
        print("Usage: plox [script]")
        sys.exit(64)
    elif len(sys.argv) == 1:
        lox.run(open(sys.argv[1]).read())
        if lox.had_error:
            sys.exit(65)
    else:
        lox.run_prompt()
