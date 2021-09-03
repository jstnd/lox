from tokens import Token, TokenType


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []

        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> list[Token]:
        while not self.at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        pass

    def at_end(self) -> bool:
        return self.current >= len(self.source)
