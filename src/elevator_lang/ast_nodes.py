"""Nodos del árbol de sintaxis abstracta (AST) de ElevatorLang.

Cada nodo guarda su posición (línea y columna) y expone ``accept`` para el patrón
visitor: la doble despacho delega en el método ``visit_*`` correspondiente del
visitante. Las expresiones y las sentencias tienen una base propia para poder
anotarlas por separado.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from elevator_lang.tokens import TokenType

if TYPE_CHECKING:
    from elevator_lang.visitor import Visitor


@dataclass
class Node:
    """Base de todos los nodos del AST; guarda la posición en el código fuente."""

    line: int
    column: int

    def accept[T](self, visitor: Visitor[T]) -> T:
        raise NotImplementedError


@dataclass
class Expression(Node):
    """Base de las expresiones."""


@dataclass
class Statement(Node):
    """Base de las sentencias."""


# --- Expresiones ---


@dataclass
class Literal(Expression):
    """Literal numérico, de texto o booleano."""

    # Nota: en Python ``bool`` es subtipo de ``int``; el análisis semántico debe
    # comprobar ``isinstance(value, bool)`` antes que ``int`` para no confundir
    # un booleano con un número.
    value: int | float | str | bool

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_literal(self)


@dataclass
class Variable(Expression):
    """Referencia a una variable por su nombre."""

    name: str

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_variable(self)


@dataclass
class Unary(Expression):
    """Operación unaria: ``-`` (negativo) o ``no`` (negación lógica)."""

    operator: TokenType
    operand: Expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_unary(self)


@dataclass
class Binary(Expression):
    """Operación binaria (aritmética, relacional, de igualdad o lógica)."""

    left: Expression
    operator: TokenType
    right: Expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_binary(self)


@dataclass
class Grouping(Expression):
    """Expresión entre paréntesis."""

    expression: Expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_grouping(self)


# --- Sentencias ---


@dataclass
class Block(Statement):
    """Bloque de sentencias entre llaves; introduce un ámbito anidado."""

    statements: list[Statement]

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_block(self)


@dataclass
class AscensorDecl(Statement):
    """Declaración del ascensor: ``ascensor A pisos N;``."""

    name: str
    floors: Expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_ascensor_decl(self)


@dataclass
class VarDecl(Statement):
    """Declaración de variable con tipo y un inicializador opcional."""

    name: str
    declared_type: TokenType
    initializer: Expression | None

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_var_decl(self)


@dataclass
class Assign(Statement):
    """Asignación a una variable existente: ``x = expr;``."""

    name: str
    value: Expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_assign(self)


@dataclass
class ElevatorCommand(Statement):
    """Comando del ascensor: subir, bajar, ir_a, abrir, cerrar o esperar.

    ``argument`` es la expresión de pisos o segundos; es ``None`` para ``abrir`` y
    ``cerrar``, que no llevan argumento.
    """

    operator: TokenType
    argument: Expression | None

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_elevator_command(self)


@dataclass
class PrintStatement(Statement):
    """Sentencia de impresión: ``imprimir expr;``."""

    expression: Expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_print_statement(self)


@dataclass
class IfStatement(Statement):
    """Condicional ``si`` con bloque ``sino`` opcional."""

    condition: Expression
    then_block: Block
    else_block: Block | None

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_if_statement(self)


@dataclass
class WhileStatement(Statement):
    """Bucle ``mientras``."""

    condition: Expression
    body: Block

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_while_statement(self)


@dataclass
class ForStatement(Statement):
    """Bucle contado ``para i desde A hasta B { ... }``."""

    variable: str
    start: Expression
    end: Expression
    body: Block

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_for_statement(self)


@dataclass
class Program(Node):
    """Nodo raíz: la secuencia de sentencias del programa."""

    statements: list[Statement]

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_program(self)
