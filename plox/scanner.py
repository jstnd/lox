from typing import Any

from tokens import Token, TokenType
from lox import Lox


class Scanner:
    def __init__(self, source: str, interpreter: Lox):
        self.source = source
        self.interpreter = interpreter

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
            case _: self.interpreter.error(self.line, "Unexpected character.")

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def add_token(self, type: TokenType, literal: Any = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if self.at_end() or self.source[self.current] != expected:
            return False

        self.current += 1
        return True
