"""Analizador semántico de ElevatorLang.

Recorre el AST con el patrón visitor y comprueba: declaración y uso de variables
en ámbitos anidados, compatibilidad de tipos en expresiones y asignaciones, y las
tres reglas del dominio del ascensor (rango de pisos, puerta cerrada para mover y
movimiento positivo) mediante una simulación abstracta del estado del ascensor.
"""

from __future__ import annotations

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
    Node,
    PrintStatement,
    Program,
    Unary,
    VarDecl,
    Variable,
    WhileStatement,
)
from elevator_lang.elevator_state import Door, ElevatorState
from elevator_lang.errors import ElevatorLangError, ErrorCollector, SemanticError
from elevator_lang.symbols import Scope, Symbol, SymbolType, symbol_type_for
from elevator_lang.tokens import MOVEMENT_COMMANDS, TokenType
from elevator_lang.visitor import Visitor

# Agrupación de operadores binarios por la categoría de tipos que exigen.
_ARITHMETIC: frozenset[TokenType] = frozenset(
    {TokenType.MAS, TokenType.MENOS, TokenType.POR, TokenType.ENTRE}
)
_RELATIONAL: frozenset[TokenType] = frozenset(
    {TokenType.MENOR, TokenType.MAYOR, TokenType.MENOR_IGUAL, TokenType.MAYOR_IGUAL}
)
_LOGICAL: frozenset[TokenType] = frozenset({TokenType.Y, TokenType.O})


def _const_number(expr: Expression | None) -> int | float | None:
    """Evalúa ``expr`` si es una constante numérica; si no, devuelve ``None``."""
    if isinstance(expr, Literal):
        value = expr.value
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return value
        return None
    if isinstance(expr, Grouping):
        return _const_number(expr.expression)
    if isinstance(expr, Unary):
        if expr.operator is TokenType.MENOS:
            operand = _const_number(expr.operand)
            return None if operand is None else -operand
        return None
    if isinstance(expr, Binary):
        left = _const_number(expr.left)
        right = _const_number(expr.right)
        if left is None or right is None:
            return None
        return _apply_arithmetic(expr.operator, left, right)
    return None


def _apply_arithmetic(
    operator: TokenType, left: int | float, right: int | float
) -> int | float | None:
    if operator is TokenType.MAS:
        return left + right
    if operator is TokenType.MENOS:
        return left - right
    if operator is TokenType.POR:
        return left * right
    if operator is TokenType.ENTRE:
        if right == 0:
            return None
        return left / right
    return None


def _as_int(value: int | float | None) -> int | None:
    """Convierte un número entero (o decimal entero) a ``int``; si no, ``None``."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


class SemanticAnalyzer(Visitor[SymbolType | None]):
    """Análisis semántico: ámbitos, tipos y reglas del dominio del ascensor."""

    def __init__(self) -> None:
        self._scope = Scope()
        self._state = ElevatorState()
        self._collector = ErrorCollector()

    @property
    def errors(self) -> list[ElevatorLangError]:
        """Errores semánticos recolectados durante el análisis."""
        return self._collector.errors

    def analyze(self, program: Program) -> None:
        """Recorre el programa aplicando las comprobaciones semánticas."""
        program.accept(self)

    # --- Sentencias ---

    def visit_program(self, node: Program) -> SymbolType | None:
        for statement in node.statements:
            statement.accept(self)
        return None

    def visit_block(self, node: Block) -> SymbolType | None:
        self._push_scope()
        for statement in node.statements:
            statement.accept(self)
        self._pop_scope()
        return None

    def visit_var_decl(self, node: VarDecl) -> SymbolType | None:
        declared_type = symbol_type_for(node.declared_type)
        if node.initializer is not None:
            value_type = node.initializer.accept(self)
            if value_type is not None and value_type is not declared_type:
                self._error(
                    node,
                    messages.assignment_type_mismatch(
                        value_type.value, node.name, declared_type.value
                    ),
                )
        symbol = Symbol(
            node.name,
            declared_type,
            node.initializer is not None,
            node.line,
            node.column,
        )
        if not self._scope.declare(symbol):
            self._error(node, messages.redeclared_variable(node.name))
        return None

    def visit_assign(self, node: Assign) -> SymbolType | None:
        symbol = self._scope.resolve(node.name)
        value_type = node.value.accept(self)
        if symbol is None:
            self._error(node, messages.undeclared_variable(node.name))
            return None
        if value_type is not None and value_type is not symbol.type:
            self._error(
                node,
                messages.assignment_type_mismatch(
                    value_type.value, node.name, symbol.type.value
                ),
            )
        symbol.initialized = True
        return None

    def visit_ascensor_decl(self, node: AscensorDecl) -> SymbolType | None:
        floors_type = node.floors.accept(self)
        if floors_type is not None and floors_type is not SymbolType.NUMERO:
            self._error(node, messages.floors_not_numeric(floors_type.value))
        if self._state.declared:
            self._error(node, messages.ascensor_already_declared())
            return None
        raw = _const_number(node.floors)
        max_floor = _as_int(raw)
        if raw is None:
            # No es una constante: el rango queda desconocido, sin error.
            self._state.declare(None)
        elif max_floor is None or max_floor <= 0:
            # Constante conocida que no es un entero positivo: viola la regla.
            self._error(node, messages.floors_not_positive())
            self._state.declare(None)
        else:
            self._state.declare(max_floor)
        return None

    def visit_elevator_command(self, node: ElevatorCommand) -> SymbolType | None:
        if node.argument is not None:
            arg_type = node.argument.accept(self)
            if arg_type is not None and arg_type is not SymbolType.NUMERO:
                self._error(
                    node,
                    messages.command_arg_not_numeric(node.operator.value, arg_type.value),
                )
        if not self._state.declared:
            self._error(node, messages.no_ascensor())
            return None
        operator = node.operator
        if operator in MOVEMENT_COMMANDS and self._state.door is Door.OPEN:
            self._error(node, messages.move_with_open_door())
        if operator is TokenType.IR_A:
            self._handle_goto(node)
        elif operator is TokenType.SUBIR:
            self._handle_move(node, ascending=True)
        elif operator is TokenType.BAJAR:
            self._handle_move(node, ascending=False)
        elif operator is TokenType.ABRIR:
            self._state.open_door()
        elif operator is TokenType.CERRAR:
            self._state.close_door()
        elif operator is TokenType.ESPERAR:
            self._handle_wait(node)
        return None

    def visit_print_statement(self, node: PrintStatement) -> SymbolType | None:
        node.expression.accept(self)  # cualquier tipo es imprimible
        return None

    def visit_if_statement(self, node: IfStatement) -> SymbolType | None:
        self._check_boolean(node.condition)
        entry = self._state
        self._state = entry.copy()
        node.then_block.accept(self)
        then_state = self._state
        if node.else_block is not None:
            self._state = entry.copy()
            node.else_block.accept(self)
            self._state = ElevatorState.join(then_state, self._state)
        else:
            self._state = ElevatorState.join(then_state, entry)
        return None

    def visit_while_statement(self, node: WhileStatement) -> SymbolType | None:
        self._check_boolean(node.condition)
        entry = self._state
        self._state = entry.copy()
        node.body.accept(self)
        self._state = ElevatorState.join(entry, self._state)
        return None

    def visit_for_statement(self, node: ForStatement) -> SymbolType | None:
        self._check_numeric_bound(node.start)
        self._check_numeric_bound(node.end)
        self._push_scope()
        loop_variable = Symbol(
            node.variable, SymbolType.NUMERO, True, node.line, node.column
        )
        self._scope.declare(loop_variable)
        entry = self._state
        self._state = entry.copy()
        node.body.accept(self)
        self._state = ElevatorState.join(entry, self._state)
        self._pop_scope()
        return None

    # --- Expresiones ---

    def visit_literal(self, node: Literal) -> SymbolType | None:
        value = node.value
        if isinstance(value, bool):
            return SymbolType.BOOLEANO
        if isinstance(value, (int, float)):
            return SymbolType.NUMERO
        return SymbolType.TEXTO

    def visit_variable(self, node: Variable) -> SymbolType | None:
        symbol = self._scope.resolve(node.name)
        if symbol is None:
            self._error(node, messages.undeclared_variable(node.name))
            return None
        if not symbol.initialized:
            self._error(node, messages.use_before_assignment(node.name))
        return symbol.type

    def visit_unary(self, node: Unary) -> SymbolType | None:
        operand_type = node.operand.accept(self)
        expected = (
            SymbolType.NUMERO if node.operator is TokenType.MENOS else SymbolType.BOOLEANO
        )
        if operand_type is not None and operand_type is not expected:
            self._error(
                node, messages.unary_type_error(expected.value, operand_type.value)
            )
        return expected

    def visit_binary(self, node: Binary) -> SymbolType | None:
        left = node.left.accept(self)
        right = node.right.accept(self)
        operator = node.operator
        if operator in _ARITHMETIC:
            self._check_binary(node, left, right, SymbolType.NUMERO)
            return SymbolType.NUMERO
        if operator in _RELATIONAL:
            self._check_binary(node, left, right, SymbolType.NUMERO)
            return SymbolType.BOOLEANO
        if operator in _LOGICAL:
            self._check_binary(node, left, right, SymbolType.BOOLEANO)
            return SymbolType.BOOLEANO
        # Igualdad (== / !=): ambos operandos deben ser del mismo tipo.
        if left is not None and right is not None and left is not right:
            self._error(node, messages.binary_type_error(left.value, right.value))
        return SymbolType.BOOLEANO

    def visit_grouping(self, node: Grouping) -> SymbolType | None:
        return node.expression.accept(self)

    # --- Auxiliares de tipos ---

    def _check_binary(
        self,
        node: Node,
        left: SymbolType | None,
        right: SymbolType | None,
        expected: SymbolType,
    ) -> None:
        if left is None or right is None:
            return
        if left is not expected or right is not expected:
            self._error(node, messages.operand_type_error(expected.value))

    def _check_boolean(self, expr: Expression) -> None:
        expr_type = expr.accept(self)
        if expr_type is not None and expr_type is not SymbolType.BOOLEANO:
            self._error(expr, messages.condition_not_boolean(expr_type.value))

    def _check_numeric_bound(self, expr: Expression) -> None:
        expr_type = expr.accept(self)
        if expr_type is not None and expr_type is not SymbolType.NUMERO:
            self._error(expr, messages.bound_not_numeric(expr_type.value))

    # --- Reglas del dominio (ascensor) ---

    def _handle_goto(self, node: ElevatorCommand) -> None:
        target = _as_int(_const_number(node.argument))
        if target is None:
            self._state.mark_floor_unknown()
            return
        if self._state.range_known and not (0 <= target <= self._state.max_floor):
            self._error(node, messages.goto_out_of_range(target, self._state.max_floor))
            self._state.mark_floor_unknown()
            return
        self._state.set_floor(target)

    def _handle_move(self, node: ElevatorCommand, *, ascending: bool) -> None:
        raw = _const_number(node.argument)
        if raw is not None and raw <= 0:
            self._error(node, messages.move_not_positive(node.operator.value))
            return
        delta = _as_int(raw)
        floor = self._state.floor
        if delta is None or not isinstance(floor, int):
            self._state.mark_floor_unknown()
            return
        new_floor = floor + delta if ascending else floor - delta
        if self._state.range_known and not (0 <= new_floor <= self._state.max_floor):
            self._error(
                node,
                messages.move_out_of_range(
                    floor, node.operator.value, delta, self._state.max_floor
                ),
            )
            self._state.mark_floor_unknown()
            return
        self._state.set_floor(new_floor)

    def _handle_wait(self, node: ElevatorCommand) -> None:
        seconds = _const_number(node.argument)
        if seconds is not None and seconds <= 0:
            self._error(node, messages.wait_not_positive())

    # --- Ámbitos y errores ---

    def _push_scope(self) -> None:
        self._scope = Scope(self._scope)

    def _pop_scope(self) -> None:
        parent = self._scope.parent
        if parent is not None:
            self._scope = parent

    def _error(self, node: Node, description: str) -> None:
        self._collector.add(SemanticError(node.line, node.column, description))
