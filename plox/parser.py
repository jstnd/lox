from __future__ import annotations

from typing import TYPE_CHECKING, Final, Optional

from .errors import LoxErrors, ParseError
from .expr import Assign, Binary, Call, Get, Grouping, Literal, Logical, Set, Unary, Variable
from .stmt import Block, Class, Expression, Function, If, Print, Return, Var, While
from .tokens import TokenType

if TYPE_CHECKING:
    from .expr import Expr
    from .stmt import Stmt
    from .tokens import Token


class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens: Final = tokens
        self._current = 0

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while not self._at_end():
            statements.append(self._declaration())

        return statements

    def _expression(self) -> Expr:
        return self._assignment()

    def _declaration(self) -> Optional[Stmt]:
        try:
            if self._match(TokenType.CLASS):
                return self._class_declaration()

            if self._match(TokenType.FUN):
                return self._function("function")

            if self._match(TokenType.VAR):
                return self._var_declaration()

            return self._statement()
        except ParseError:
            self._synchronize()

    def _class_declaration(self) -> Stmt:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect class name.")
        self._consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods: list[Function] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            methods.append(self._function("method"))

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, methods)

    def _statement(self) -> Stmt:
        if self._match(TokenType.FOR):
            return self._for_statement()

        if self._match(TokenType.IF):
            return self._if_statement()

        if self._match(TokenType.PRINT):
            return self._print_statement()

        if self._match(TokenType.RETURN):
            return self._return_statement()

        if self._match(TokenType.WHILE):
            return self._while_statement()

        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())

        return self._expression_statement()

    def _for_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Optional[Stmt]
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Optional[Expr] = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Stmt = self._statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def _expression_statement(self) -> Stmt:
        value: Expr = self._expression()  # parse subsequent expression
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")  # consume terminating semicolon
        return Expression(value)  # emit stmt.Expression syntax tree

    def _function(self, kind: str) -> Function:
        name: Token = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")

        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        parameters: list[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self._error(self._peek(), "Can't have more than 255 parameters.")

                parameters.append(self._consume(TokenType.IDENTIFIER, "Expect parameter name."))

                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self._consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")

        body: list[Stmt] = self._block()

        return Function(name, parameters, body)

    def _if_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self._statement()
        else_branch: Optional[Stmt] = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return If(condition, then_branch, else_branch)

    def _print_statement(self) -> Stmt:
        value: Expr = self._expression()  # parse subsequent expression
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")  # consume terminating semicolon
        return Print(value)  # emit stmt.Print syntax tree

    def _return_statement(self) -> Stmt:
        keyword: Token = self._previous()
        value: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def _var_declaration(self) -> Stmt:
        name: Token = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: Optional[Expr] = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _while_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        body: Stmt = self._statement()

        return While(condition, body)

    def _block(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _assignment(self) -> Expr:
        expr: Expr = self._or()

        if self._match(TokenType.EQUAL):
            equals: Token = self._previous()
            value: Expr = self._assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.obj, expr.name, value)

            self._error(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expr:
        expr: Expr = self._and()

        while self._match(TokenType.OR):
            operator: Token = self._previous()
            right: Expr = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        expr: Expr = self._equality()

        while self._match(TokenType.AND):
            operator: Token = self._previous()
            right: Expr = self._equality()
            expr = Logical(expr, operator, right)

        return expr

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

        return self._call()

    def _call(self) -> Expr:
        expr: Expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name: Token = self._consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        paren: Token = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)

        if self._match(TokenType.TRUE):
            return Literal(True)

        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr: Expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

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
