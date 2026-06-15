"""Pruebas del analizador sintáctico (Fase 2).

Verifican la forma del AST por construcción, la precedencia de operadores, el
programa de ejemplo válido, los errores sintácticos con su posición, la
recuperación en modo pánico y el despacho del patrón visitor.
"""

from __future__ import annotations

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
    Unary,
    VarDecl,
    Variable,
    WhileStatement,
)
from elevator_lang.errors import ElevatorLangError
from elevator_lang.lexer import Lexer
from elevator_lang.parser import Parser
from elevator_lang.tokens import TokenType
from elevator_lang.visitor import Visitor


def _parse(source: str) -> tuple[Program, list[ElevatorLangError]]:
    """Tokeniza y analiza ``source``; devuelve el programa y los errores."""
    tokens = Lexer(source).scan_tokens()
    parser = Parser(tokens)
    return parser.parse(), parser.errors


def _first_print_expr(program: Program) -> Expression:
    """Devuelve la expresión de la primera sentencia ``imprimir``."""
    statement = program.statements[0]
    assert isinstance(statement, PrintStatement)
    return statement.expression


# --- Precedencia de expresiones ---


def test_multiplication_binds_tighter_than_addition() -> None:
    program, errors = _parse("imprimir 1 + 2 * 3;")
    assert errors == []
    expr = _first_print_expr(program)
    assert isinstance(expr, Binary)
    assert expr.operator is TokenType.MAS
    assert isinstance(expr.right, Binary)
    assert expr.right.operator is TokenType.POR


def test_comparison_binds_looser_than_arithmetic() -> None:
    expr = _first_print_expr(_parse("imprimir 1 + 2 < 5;")[0])
    assert isinstance(expr, Binary)
    assert expr.operator is TokenType.MENOR
    assert isinstance(expr.left, Binary)
    assert expr.left.operator is TokenType.MAS


def test_and_binds_tighter_than_or() -> None:
    expr = _first_print_expr(_parse("imprimir verdadero o falso y verdadero;")[0])
    assert isinstance(expr, Binary)
    assert expr.operator is TokenType.O
    assert isinstance(expr.right, Binary)
    assert expr.right.operator is TokenType.Y


def test_unary_and_grouping() -> None:
    expr = _first_print_expr(_parse("imprimir -(1 + 2);")[0])
    assert isinstance(expr, Unary)
    assert expr.operator is TokenType.MENOS
    assert isinstance(expr.operand, Grouping)
    assert isinstance(expr.operand.expression, Binary)


# --- Sentencias ---


def test_ascensor_declaration() -> None:
    program, errors = _parse("ascensor A pisos 10;")
    assert errors == []
    decl = program.statements[0]
    assert isinstance(decl, AscensorDecl)
    assert decl.name == "A"
    assert isinstance(decl.floors, Literal)
    assert decl.floors.value == 10


def test_var_declaration_with_type_and_initializer() -> None:
    decl = _parse("var x : numero = 5;")[0].statements[0]
    assert isinstance(decl, VarDecl)
    assert decl.name == "x"
    assert decl.declared_type is TokenType.NUMERO
    assert isinstance(decl.initializer, Literal)
    assert decl.initializer.value == 5


def test_var_declaration_without_initializer() -> None:
    decl = _parse("var listo : booleano;")[0].statements[0]
    assert isinstance(decl, VarDecl)
    assert decl.declared_type is TokenType.BOOLEANO
    assert decl.initializer is None


def test_assignment() -> None:
    statement = _parse("x = 3 + 4;")[0].statements[0]
    assert isinstance(statement, Assign)
    assert statement.name == "x"
    assert isinstance(statement.value, Binary)


def test_movement_command_has_argument() -> None:
    command = _parse("subir 3;")[0].statements[0]
    assert isinstance(command, ElevatorCommand)
    assert command.operator is TokenType.SUBIR
    assert isinstance(command.argument, Literal)
    assert command.argument.value == 3


def test_door_command_has_no_argument() -> None:
    command = _parse("abrir;")[0].statements[0]
    assert isinstance(command, ElevatorCommand)
    assert command.operator is TokenType.ABRIR
    assert command.argument is None


def test_wait_command_consumes_segundos() -> None:
    program, errors = _parse("esperar 5 segundos;")
    assert errors == []
    command = program.statements[0]
    assert isinstance(command, ElevatorCommand)
    assert command.operator is TokenType.ESPERAR
    assert isinstance(command.argument, Literal)
    assert command.argument.value == 5


def test_if_else() -> None:
    statement = _parse("si x > 0 { abrir; } sino { cerrar; }")[0].statements[0]
    assert isinstance(statement, IfStatement)
    assert isinstance(statement.condition, Binary)
    assert isinstance(statement.then_block, Block)
    assert len(statement.then_block.statements) == 1
    assert statement.else_block is not None
    assert len(statement.else_block.statements) == 1


def test_if_without_else() -> None:
    statement = _parse("si x > 0 { abrir; }")[0].statements[0]
    assert isinstance(statement, IfStatement)
    assert statement.else_block is None


def test_while() -> None:
    statement = _parse("mientras x < 10 { subir 1; }")[0].statements[0]
    assert isinstance(statement, WhileStatement)
    assert isinstance(statement.condition, Binary)
    assert len(statement.body.statements) == 1


def test_for() -> None:
    statement = _parse("para i desde 0 hasta 4 { abrir; }")[0].statements[0]
    assert isinstance(statement, ForStatement)
    assert statement.variable == "i"
    assert isinstance(statement.start, Literal)
    assert isinstance(statement.end, Literal)
    assert len(statement.body.statements) == 1


def test_print_statement() -> None:
    statement = _parse('imprimir "hola";')[0].statements[0]
    assert isinstance(statement, PrintStatement)
    assert isinstance(statement.expression, Literal)
    assert statement.expression.value == "hola"


# --- Programa de ejemplo válido ---


def test_valid_sample_program_parses_clean() -> None:
    source = (
        "ascensor A pisos 10;\n"
        "ir_a 5;\n"
        "abrir;\n"
        "esperar 3 segundos;\n"
        "cerrar;\n"
        "subir 2;\n"
        "abrir;\n"
    )
    program, errors = _parse(source)
    assert errors == []
    assert len(program.statements) == 7


# --- Errores sintácticos ---


def test_missing_semicolon_reports_position_and_message() -> None:
    _program, errors = _parse("ascensor A pisos 10\nir_a 5;\n")
    error = errors[0]
    assert (error.line, error.column) == (2, 1)
    assert error.description == "se esperaba ';', se encontró 'ir_a'"
    assert str(error).startswith("Error sintáctico [línea 2, columna 1]:")


def test_missing_brace_in_if_is_reported() -> None:
    _program, errors = _parse("si x > 0 abrir; }")
    assert errors[0].description == "se esperaba '{', se encontró 'abrir'"


def test_missing_expression_is_reported() -> None:
    _program, errors = _parse("imprimir ;")
    assert errors[0].description == "se esperaba una expresión, se encontró ';'"


def test_unexpected_statement_is_reported() -> None:
    _program, errors = _parse("123;")
    assert errors[0].description == "se esperaba una sentencia, se encontró '123'"


# --- Recuperación en modo pánico ---


def test_panic_recovery_collects_multiple_errors() -> None:
    _program, errors = _parse("var x : numero = ;\nvar y : numero = ;\n")
    assert len(errors) == 2


def test_recovery_continues_to_next_valid_statement() -> None:
    program, errors = _parse("imprimir ;\nabrir;\n")
    assert len(errors) == 1
    assert any(isinstance(s, ElevatorCommand) for s in program.statements)


# --- Patrón visitor ---


class _NodeCounter(Visitor[int]):
    """Visitante de prueba: cuenta los nodos del subárbol."""

    def visit_literal(self, node: Literal) -> int:
        return 1

    def visit_variable(self, node: Variable) -> int:
        return 1

    def visit_unary(self, node: Unary) -> int:
        return 1 + node.operand.accept(self)

    def visit_binary(self, node: Binary) -> int:
        return 1 + node.left.accept(self) + node.right.accept(self)

    def visit_grouping(self, node: Grouping) -> int:
        return 1 + node.expression.accept(self)

    def visit_block(self, node: Block) -> int:
        return 1 + sum(statement.accept(self) for statement in node.statements)

    def visit_ascensor_decl(self, node: AscensorDecl) -> int:
        return 1 + node.floors.accept(self)

    def visit_var_decl(self, node: VarDecl) -> int:
        extra = node.initializer.accept(self) if node.initializer is not None else 0
        return 1 + extra

    def visit_assign(self, node: Assign) -> int:
        return 1 + node.value.accept(self)

    def visit_elevator_command(self, node: ElevatorCommand) -> int:
        extra = node.argument.accept(self) if node.argument is not None else 0
        return 1 + extra

    def visit_print_statement(self, node: PrintStatement) -> int:
        return 1 + node.expression.accept(self)

    def visit_if_statement(self, node: IfStatement) -> int:
        total = 1 + node.condition.accept(self) + node.then_block.accept(self)
        if node.else_block is not None:
            total += node.else_block.accept(self)
        return total

    def visit_while_statement(self, node: WhileStatement) -> int:
        return 1 + node.condition.accept(self) + node.body.accept(self)

    def visit_for_statement(self, node: ForStatement) -> int:
        return (
            1 + node.start.accept(self) + node.end.accept(self) + node.body.accept(self)
        )

    def visit_program(self, node: Program) -> int:
        return 1 + sum(statement.accept(self) for statement in node.statements)


def test_visitor_dispatch_counts_nodes() -> None:
    program, errors = _parse("subir 1 + 2;")
    assert errors == []
    # Program + ElevatorCommand + Binary + Literal + Literal = 5
    assert program.accept(_NodeCounter()) == 5


# --- Casos adicionales ---


def test_unary_is_right_associative() -> None:
    expr = _first_print_expr(_parse("imprimir no no verdadero;")[0])
    assert isinstance(expr, Unary)
    assert isinstance(expr.operand, Unary)
    assert isinstance(expr.operand.operand, Literal)


def test_empty_block() -> None:
    statement = _parse("si verdadero { }")[0].statements[0]
    assert isinstance(statement, IfStatement)
    assert statement.then_block.statements == []


def test_nested_blocks() -> None:
    statement = _parse("{ { abrir; } }")[0].statements[0]
    assert isinstance(statement, Block)
    inner = statement.statements[0]
    assert isinstance(inner, Block)
    assert len(inner.statements) == 1


def test_else_if_chain_via_nested_si() -> None:
    statement = _parse("si a { } sino { si b { } }")[0].statements[0]
    assert isinstance(statement, IfStatement)
    assert statement.else_block is not None
    nested = statement.else_block.statements[0]
    assert isinstance(nested, IfStatement)


def test_recovery_inside_block() -> None:
    program, errors = _parse("{ imprimir ; abrir; }")
    assert len(errors) == 1
    block = program.statements[0]
    assert isinstance(block, Block)
    assert any(isinstance(s, ElevatorCommand) for s in block.statements)


def test_eof_mid_statement_reports_single_error() -> None:
    _program, errors = _parse("var x : numero =")
    assert len(errors) == 1
    expected = "se esperaba una expresión, se encontró fin de archivo"
    assert errors[0].description == expected


def test_unclosed_nested_blocks_do_not_cascade() -> None:
    # Bloques anidados sin cerrar no deben producir un error por nivel.
    _program, errors = _parse("{ { {")
    assert len(errors) == 1
    assert errors[0].description == "se esperaba '}', se encontró fin de archivo"
