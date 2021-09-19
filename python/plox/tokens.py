from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    # single character tokens
    LEFT_PAREN = auto(),
    RIGHT_PAREN = auto(),
    LEFT_BRACE = auto(),
    RIGHT_BRACE = auto(),
    COMMA = auto(),
    DOT = auto(),
    MINUS = auto(),
    PLUS = auto(),
    SEMICOLON = auto(),
    SLASH = auto(),
    STAR = auto(),

    # one or two character tokens
    BANG = auto(),
    BANG_EQUAL = auto(),
    EQUAL = auto(),
    EQUAL_EQUAL = auto(),
    GREATER = auto(),
    GREATER_EQUAL = auto(),
    LESS = auto(),
    LESS_EQUAL = auto(),

    # literals
    IDENTIFIER = auto(),
    STRING = auto(),
    NUMBER = auto(),

    # keywords
    AND = auto(),
    CLASS = auto(),
    ELSE = auto(),
    FALSE = auto(),
    FUN = auto(),
    FOR = auto(),
    IF = auto(),
    NIL = auto(),
    OR = auto(),
    PRINT = auto(),
    RETURN = auto(),
    SUPER = auto(),
    THIS = auto(),
    TRUE = auto(),
    VAR = auto(),
    WHILE = auto(),

    EOF = auto()


class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: Any, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"
