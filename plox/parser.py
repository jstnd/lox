from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .errors import LoxErrors, ParseError
from .expr import Binary, Grouping, Literal, Unary
from .tokens import TokenType

if TYPE_CHECKING:
    from .expr import Expr
    from .tokens import Token


class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens: Final = tokens
        self._current = 0

    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr: Expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self._previous()
            right: Expr = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr: Expr = self._term()

        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self._previous()
            right: Expr = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr: Expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self._previous()
            right: Expr = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr: Expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self._previous()
            right: Expr = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self._previous()
            right: Expr = self._unary()
            return Unary(operator, right)

        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)

        if self._match(TokenType.TRUE):
            return Literal(True)

        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr: Expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

    def _consume(self, type: TokenType, message: str):
        if self._check(type):
            return self._advance()

        raise self._error(self._peek(), message)

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True

        return False

    def _check(self, type: TokenType) -> bool:
        if self._at_end():
            return False
        return self._peek().type == type

    def _advance(self) -> Token:
        if not self._at_end():
            self._current += 1
        return self._previous()

    def _at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    def _error(self, token: Token, message: str) -> ParseError:
        LoxErrors.token_error(token, message)
        return ParseError()

    def _synchronize(self) -> None:
        self._advance()

        while not self._at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return

            match self._peek().type:
                case TokenType.CLASS | TokenType.FUN | TokenType.VAR | TokenType.FOR\
                     | TokenType.IF | TokenType.WHILE | TokenType.PRINT | TokenType.RETURN:
                    return

            self._advance()
