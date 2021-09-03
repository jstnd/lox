from typing import Any

from errors import LoxErrors
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

    def at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self) -> None:
        c: str = self.advance()
        match c:
            case "(": self.add_token(TokenType.LEFT_PAREN)
            case ")": self.add_token(TokenType.RIGHT_PAREN)
            case "{": self.add_token(TokenType.LEFT_BRACE)
            case "}": self.add_token(TokenType.RIGHT_BRACE)
            case ",": self.add_token(TokenType.COMMA)
            case ".": self.add_token(TokenType.DOT)
            case "-": self.add_token(TokenType.MINUS)
            case "+": self.add_token(TokenType.PLUS)
            case "*": self.add_token(TokenType.STAR)
            case "!": self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
            case "=": self.add_token(TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL)
            case "<": self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
            case ">": self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
            case "/":
                if self.match("/"):  # COMMENT
                    while self.peek() != "\n" and not self.at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t": pass  # IGNORE WHITESPACE
            case "\n": self.line += 1
            case '"': self.string()
            case _:
                if self.is_digit(c):
                    self.number()
                else:
                    LoxErrors.error(self.line, "Unexpected character.")

    def add_token(self, type: TokenType, literal: Any = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def match(self, expected: str) -> bool:
        if self.at_end() or self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.at_end():
            return "\0"

        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def is_digit(self, c: str) -> bool:
        return "0" <= c <= "9"

    def string(self) -> None:
        while self.peek() != '"' and not self.at_end():
            if self.peek() == "\n":
                self.line += 1

            self.advance()

        if self.at_end():
            LoxErrors.error(self.line, "Unterminated string.")
            return

        # closing "
        self.advance()

        # trim surrounding quotes
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()  # consume "."

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))
