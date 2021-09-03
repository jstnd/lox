class LoxErrors:
    had_error = False

    @staticmethod
    def error(line: int, message: str):
        LoxErrors.report(line, "", message)

    @staticmethod
    def report(line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        LoxErrors.had_error = True
