"""Analizador sintáctico de ElevatorLang.

Parser descendente recursivo que consume la lista de tokens del lexer y
construye un AST explícito siguiendo ``docs/gramatica.ebnf``. Ante un error
sintáctico entra en modo pánico: reporta el problema, sincroniza hasta el
siguiente límite de sentencia y continúa, de modo que recolecta varios errores
en una sola pasada.
"""

from __future__ import annotations

from collections.abc import Callable

from elevator_lang import messages
from elevator_lang.ast_nodes import (
    AscensorDecl,
    Assign,
    Binary,
    Block,
    ElevatorCommand,
    Expression,
    ForStatement,
    Grouping,
    IfStatement,
    Literal,
    PrintStatement,
    Program,
    Statement,
    Unary,
    VarDecl,
    Variable,
    WhileStatement,
)
from elevator_lang.errors import ElevatorLangError, ErrorCollector, SyntacticError
from elevator_lang.tokens import Token, TokenType

# Comandos del ascensor y, de ellos, los que llevan un argumento de movimiento.
_ELEVATOR_COMMANDS: frozenset[TokenType] = frozenset(
    {
        TokenType.SUBIR,
        TokenType.BAJAR,
        TokenType.IR_A,
        TokenType.ABRIR,
        TokenType.CERRAR,
        TokenType.ESPERAR,
    }
)
_MOVEMENT_COMMANDS: frozenset[TokenType] = frozenset(
    {TokenType.SUBIR, TokenType.BAJAR, TokenType.IR_A}
)

# Tokens que nombran un tipo del dominio.
_TYPE_TOKENS: frozenset[TokenType] = frozenset(
    {TokenType.NUMERO, TokenType.BOOLEANO, TokenType.TEXTO}
)

# Tokens con los que puede comenzar una sentencia; sirven para sincronizar tras
# un error (modo pánico).
_STATEMENT_STARTERS: frozenset[TokenType] = (
    frozenset(
        {
            TokenType.ASCENSOR,
            TokenType.VAR,
            TokenType.SI,
            TokenType.MIENTRAS,
            TokenType.PARA,
            TokenType.IMPRIMIR,
            TokenType.LLAVE_IZQ,
        }
    )
    | _ELEVATOR_COMMANDS
)
_SYNC_POINTS: frozenset[TokenType] = _STATEMENT_STARTERS | frozenset(
    {TokenType.LLAVE_DER}
)


class _ParseError(Exception):
    """Señal interna del modo pánico; nunca escapa del parser."""


class Parser:
    """Analizador sintáctico descendente recursivo que construye el AST."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._current = 0
        self._collector = ErrorCollector()

    @property
    def errors(self) -> list[ElevatorLangError]:
        """Errores sintácticos recolectados durante el análisis."""
        return self._collector.errors

    def parse(self) -> Program:
        """Analiza el programa completo y devuelve el nodo raíz."""
        first = self._peek()
        statements: list[Statement] = []
        while not self._at_end():
            statement = self._declaration()
            if statement is not None:
                statements.append(statement)
        return Program(first.line, first.column, statements)

    # --- Sentencias ---

    def _declaration(self) -> Statement | None:
        try:
            return self._statement()
        except _ParseError:
            self._synchronize()
            return None

    def _statement(self) -> Statement:
        token_type = self._peek().type
        if token_type is TokenType.ASCENSOR:
            return self._ascensor_declaration()
        if token_type is TokenType.VAR:
            return self._var_declaration()
        if token_type is TokenType.SI:
            return self._if_statement()
        if token_type is TokenType.MIENTRAS:
            return self._while_statement()
        if token_type is TokenType.PARA:
            return self._for_statement()
        if token_type is TokenType.IMPRIMIR:
            return self._print_statement()
        if token_type is TokenType.LLAVE_IZQ:
            return self._block()
        if token_type in _ELEVATOR_COMMANDS:
            return self._elevator_command()
        if token_type is TokenType.IDENTIFICADOR:
            return self._assignment()
        raise self._error(
            self._peek(),
            messages.syntax_expected(messages.EXPECTED_STATEMENT, self._found()),
        )

    def _ascensor_declaration(self) -> AscensorDecl:
        keyword = self._advance()
        name = self._consume(TokenType.IDENTIFICADOR, messages.EXPECTED_IDENTIFIER)
        self._consume_symbol(TokenType.PISOS)
        floors = self._expression()
        self._consume_symbol(TokenType.PUNTO_COMA)
        return AscensorDecl(keyword.line, keyword.column, name.lexeme, floors)

    def _var_declaration(self) -> VarDecl:
        keyword = self._advance()
        name = self._consume(TokenType.IDENTIFICADOR, messages.EXPECTED_IDENTIFIER)
        self._consume_symbol(TokenType.DOS_PUNTOS)
        declared_type = self._consume_type()
        initializer: Expression | None = None
        if self._match(TokenType.ASIGNAR):
            initializer = self._expression()
        self._consume_symbol(TokenType.PUNTO_COMA)
        return VarDecl(
            keyword.line, keyword.column, name.lexeme, declared_type, initializer
        )

    def _assignment(self) -> Assign:
        name = self._advance()
        self._consume_symbol(TokenType.ASIGNAR)
        value = self._expression()
        self._consume_symbol(TokenType.PUNTO_COMA)
        return Assign(name.line, name.column, name.lexeme, value)

    def _elevator_command(self) -> ElevatorCommand:
        operator = self._advance()
        argument: Expression | None = None
        if operator.type in _MOVEMENT_COMMANDS:
            argument = self._expression()
        elif operator.type is TokenType.ESPERAR:
            argument = self._expression()
            self._consume_symbol(TokenType.SEGUNDOS)
        self._consume_symbol(TokenType.PUNTO_COMA)
        return ElevatorCommand(operator.line, operator.column, operator.type, argument)

    def _print_statement(self) -> PrintStatement:
        keyword = self._advance()
        expression = self._expression()
        self._consume_symbol(TokenType.PUNTO_COMA)
        return PrintStatement(keyword.line, keyword.column, expression)

    def _if_statement(self) -> IfStatement:
        keyword = self._advance()
        condition = self._expression()
        then_block = self._block()
        else_block: Block | None = None
        if self._match(TokenType.SINO):
            else_block = self._block()
        return IfStatement(
            keyword.line, keyword.column, condition, then_block, else_block
        )

    def _while_statement(self) -> WhileStatement:
        keyword = self._advance()
        condition = self._expression()
        body = self._block()
        return WhileStatement(keyword.line, keyword.column, condition, body)

    def _for_statement(self) -> ForStatement:
        keyword = self._advance()
        variable = self._consume(TokenType.IDENTIFICADOR, messages.EXPECTED_IDENTIFIER)
        self._consume_symbol(TokenType.DESDE)
        start = self._expression()
        self._consume_symbol(TokenType.HASTA)
        end = self._expression()
        body = self._block()
        return ForStatement(
            keyword.line, keyword.column, variable.lexeme, start, end, body
        )

    def _block(self) -> Block:
        opening = self._consume_symbol(TokenType.LLAVE_IZQ)
        statements: list[Statement] = []
        while not self._check(TokenType.LLAVE_DER) and not self._at_end():
            statement = self._declaration()
            if statement is not None:
                statements.append(statement)
        self._consume_symbol(TokenType.LLAVE_DER)
        return Block(opening.line, opening.column, statements)

    # --- Expresiones (de menor a mayor precedencia) ---

    def _expression(self) -> Expression:
        return self._or()

    def _or(self) -> Expression:
        return self._left_assoc(self._and, TokenType.O)

    def _and(self) -> Expression:
        return self._left_assoc(self._equality, TokenType.Y)

    def _equality(self) -> Expression:
        return self._left_assoc(self._comparison, TokenType.IGUAL, TokenType.DISTINTO)

    def _comparison(self) -> Expression:
        return self._left_assoc(
            self._term,
            TokenType.MENOR,
            TokenType.MAYOR,
            TokenType.MENOR_IGUAL,
            TokenType.MAYOR_IGUAL,
        )

    def _term(self) -> Expression:
        return self._left_assoc(self._factor, TokenType.MAS, TokenType.MENOS)

    def _factor(self) -> Expression:
        return self._left_assoc(self._unary, TokenType.POR, TokenType.ENTRE)

    def _left_assoc(
        self, next_rule: Callable[[], Expression], *operators: TokenType
    ) -> Expression:
        """Regla binaria asociativa por la izquierda parametrizada por operadores."""
        expression = next_rule()
        while self._match(*operators):
            operator = self._previous()
            right = next_rule()
            expression = Binary(
                operator.line, operator.column, expression, operator.type, right
            )
        return expression

    def _unary(self) -> Expression:
        if self._match(TokenType.NO, TokenType.MENOS):
            operator = self._previous()
            operand = self._unary()
            return Unary(operator.line, operator.column, operator.type, operand)
        return self._primary()

    def _primary(self) -> Expression:
        token = self._peek()
        if self._match(TokenType.NUMERO_LITERAL, TokenType.TEXTO_LITERAL):
            # El lexer siempre asigna un valor a estos literales.
            value = token.value
            assert value is not None
            return Literal(token.line, token.column, value)
        if self._match(TokenType.VERDADERO):
            return Literal(token.line, token.column, True)
        if self._match(TokenType.FALSO):
            return Literal(token.line, token.column, False)
        if self._match(TokenType.IDENTIFICADOR):
            return Variable(token.line, token.column, token.lexeme)
        if self._match(TokenType.PAREN_IZQ):
            inner = self._expression()
            self._consume_symbol(TokenType.PAREN_DER)
            return Grouping(token.line, token.column, inner)
        raise self._error(
            token,
            messages.syntax_expected(messages.EXPECTED_EXPRESSION, self._found()),
        )

    # --- Consumo y reconocimiento de tokens ---

    def _consume(self, token_type: TokenType, expected: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise self._error(self._peek(), messages.syntax_expected(expected, self._found()))

    def _consume_symbol(self, token_type: TokenType) -> Token:
        """Consume un token cuyo texto esperado es su propio símbolo."""
        return self._consume(token_type, messages.quoted(token_type.value))

    def _consume_type(self) -> TokenType:
        if self._peek().type in _TYPE_TOKENS:
            return self._advance().type
        raise self._error(
            self._peek(),
            messages.syntax_expected(messages.EXPECTED_TYPE, self._found()),
        )

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().type is token_type

    def _advance(self) -> Token:
        token = self._peek()
        if not self._at_end():
            self._current += 1
        return token

    def _at_end(self) -> bool:
        return self._peek().type is TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _previous(self) -> Token:
        return self._tokens[self._current - 1]

    # --- Errores y recuperación ---

    def _found(self) -> str:
        token = self._peek()
        if token.type is TokenType.EOF:
            return messages.END_OF_FILE
        return messages.quoted(token.lexeme)

    def _error(self, token: Token, description: str) -> _ParseError:
        self._collector.add(SyntacticError(token.line, token.column, description))
        return _ParseError()

    def _synchronize(self) -> None:
        self._advance()
        while not self._at_end():
            if self._previous().type is TokenType.PUNTO_COMA:
                return
            if self._peek().type in _SYNC_POINTS:
                return
            self._advance()
