"""Visitante genérico del AST (patrón visitor).

Define un método ``visit_*`` abstracto por cada nodo. Las fases que recorren el
árbol (por ejemplo, el análisis semántico) heredan de ``Visitor`` y deben
implementarlos todos; el parámetro de tipo ``T`` es el tipo que devuelve cada
visita.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from elevator_lang.ast_nodes import (
        AscensorDecl,
        Assign,
        Binary,
        Block,
        ElevatorCommand,
        ForStatement,
        Grouping,
        IfStatement,
        Literal,
        PrintStatement,
        Program,
        Unary,
        VarDecl,
        Variable,
        WhileStatement,
    )


class Visitor[T](ABC):
    """Recorre el AST despachando cada nodo a su método ``visit_*``."""

    @abstractmethod
    def visit_literal(self, node: Literal) -> T: ...

    @abstractmethod
    def visit_variable(self, node: Variable) -> T: ...

    @abstractmethod
    def visit_unary(self, node: Unary) -> T: ...

    @abstractmethod
    def visit_binary(self, node: Binary) -> T: ...

    @abstractmethod
    def visit_grouping(self, node: Grouping) -> T: ...

    @abstractmethod
    def visit_block(self, node: Block) -> T: ...

    @abstractmethod
    def visit_ascensor_decl(self, node: AscensorDecl) -> T: ...

    @abstractmethod
    def visit_var_decl(self, node: VarDecl) -> T: ...

    @abstractmethod
    def visit_assign(self, node: Assign) -> T: ...

    @abstractmethod
    def visit_elevator_command(self, node: ElevatorCommand) -> T: ...

    @abstractmethod
    def visit_print_statement(self, node: PrintStatement) -> T: ...

    @abstractmethod
    def visit_if_statement(self, node: IfStatement) -> T: ...

    @abstractmethod
    def visit_while_statement(self, node: WhileStatement) -> T: ...

    @abstractmethod
    def visit_for_statement(self, node: ForStatement) -> T: ...

    @abstractmethod
    def visit_program(self, node: Program) -> T: ...
