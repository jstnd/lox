import sys

from plox import Lox, LoxErrors

if __name__ == "__main__":
    lox = Lox()

    if len(sys.argv) > 2:
        print("Usage: lox.py [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        lox.run(open(sys.argv[1]).read())
        if LoxErrors.had_error:
            sys.exit(65)

        if LoxErrors.had_runtime_error:
            sys.exit(70)
    else:
        lox.run_prompt()
