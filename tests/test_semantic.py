"""Pruebas del analizador semántico (Fase 3).

Cubren las comprobaciones genéricas (variables no declaradas, redeclaradas, uso
antes de asignar y tipos incompatibles), el chequeo de tipos en expresiones y las
tres reglas del dominio del ascensor, además de la política de seguimiento del
estado y los ámbitos anidados.
"""

from __future__ import annotations

from elevator_lang.elevator_state import UNKNOWN, Door, ElevatorState
from elevator_lang.errors import ElevatorLangError
from elevator_lang.lexer import Lexer
from elevator_lang.parser import Parser
from elevator_lang.semantic_analyzer import SemanticAnalyzer


def _analyze(source: str) -> list[ElevatorLangError]:
    """Tokeniza, analiza y comprueba ``source``; devuelve los errores semánticos.

    Exige que el programa de prueba sea sintácticamente válido para que un error
    de sintaxis accidental no haga pasar la prueba en silencio.
    """
    tokens = Lexer(source).scan_tokens()
    parser = Parser(tokens)
    program = parser.parse()
    assert parser.errors == []
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    return analyzer.errors


# --- Comprobaciones genéricas ---


def test_undeclared_variable() -> None:
    errors = _analyze("imprimir x;")
    assert len(errors) == 1
    assert errors[0].description == "la variable 'x' no ha sido declarada"


def test_redeclared_variable() -> None:
    errors = _analyze("var x : numero = 1;\nvar x : numero = 2;")
    assert len(errors) == 1
    assert "ya fue declarada" in errors[0].description


def test_use_before_assignment() -> None:
    errors = _analyze("var x : numero;\nimprimir x;")
    assert len(errors) == 1
    assert "antes de asignarle" in errors[0].description


def test_assignment_after_declaration_is_ok() -> None:
    assert _analyze("var x : numero;\nx = 5;\nimprimir x;") == []


def test_type_mismatch_in_declaration() -> None:
    errors = _analyze("var x : numero = verdadero;")
    assert len(errors) == 1
    assert errors[0].description == (
        "no se puede asignar un valor de tipo 'booleano' a la variable "
        "'x' de tipo 'numero'"
    )


# --- Chequeo de tipos en expresiones ---


def test_arithmetic_requires_numbers() -> None:
    errors = _analyze('imprimir 1 + "hola";')
    assert len(errors) == 1
    assert "deben ser de tipo 'numero'" in errors[0].description


def test_logical_requires_booleans() -> None:
    assert len(_analyze("imprimir 1 y verdadero;")) == 1


def test_relational_yields_boolean() -> None:
    assert _analyze("var b : booleano = 3 < 5;") == []


def test_equality_requires_same_type() -> None:
    assert len(_analyze('imprimir 1 == "hola";')) == 1


def test_condition_must_be_boolean() -> None:
    errors = _analyze("si 5 { }")
    assert len(errors) == 1
    expected = "la condición debe ser de tipo 'booleano', no 'numero'"
    assert errors[0].description == expected


# --- Reglas del dominio del ascensor ---


def test_floor_range_exceeded_matches_spec() -> None:
    errors = _analyze("ascensor A pisos 5;\nir_a 3;\nsubir 10;")
    assert len(errors) == 1
    expected = "desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)"
    assert errors[0].description == expected


def test_goto_out_of_range() -> None:
    errors = _analyze("ascensor A pisos 5;\nir_a 8;")
    assert len(errors) == 1
    assert errors[0].description == "no se puede ir al piso 8: excede el rango (0..5)"


def test_bajar_below_ground() -> None:
    errors = _analyze("ascensor A pisos 10;\nir_a 3;\nbajar 5;")
    assert len(errors) == 1
    assert "excede el rango" in errors[0].description


def test_move_must_be_positive() -> None:
    errors = _analyze("ascensor A pisos 10;\nsubir -1;")
    assert len(errors) == 1
    assert errors[0].description == "el movimiento de 'subir' debe ser positivo"


def test_wait_must_be_positive() -> None:
    errors = _analyze("ascensor A pisos 10;\nesperar 0 segundos;")
    assert len(errors) == 1
    assert errors[0].description == "el tiempo de espera debe ser positivo"


def test_move_with_open_door() -> None:
    errors = _analyze("ascensor A pisos 10;\nabrir;\nsubir 2;")
    assert any("puerta abierta" in error.description for error in errors)


def test_command_before_ascensor() -> None:
    errors = _analyze("subir 2;")
    assert len(errors) == 1
    assert errors[0].description == "no hay ningún ascensor declarado"


def test_ascensor_redeclared() -> None:
    errors = _analyze("ascensor A pisos 10;\nascensor B pisos 5;")
    assert len(errors) == 1
    assert errors[0].description == "el ascensor ya fue declarado"


def test_floors_must_be_positive() -> None:
    assert any(
        "entero positivo" in e.description for e in _analyze("ascensor A pisos 0;")
    )


def test_command_arg_must_be_numeric() -> None:
    errors = _analyze('ascensor A pisos 10;\nsubir "alto";')
    assert any("debe ser de tipo 'numero'" in error.description for error in errors)


# --- Política de seguimiento del estado ---


def test_unknown_floor_after_branch_suppresses_range_check() -> None:
    # Tras un 'si' que mueve el ascensor de forma ambigua el piso es desconocido,
    # así que 'subir 100' no se comprueba (política: sin falsos positivos).
    source = "ascensor A pisos 10;\nir_a 3;\nsi 3 < 5 {\n    subir 2;\n}\nsubir 100;\n"
    assert _analyze(source) == []


def test_movement_with_variable_argument_is_untracked() -> None:
    # 'subir n' no es constante: el piso queda desconocido y 'subir 100' no se revisa.
    source = "ascensor A pisos 10;\nvar n : numero = 2;\nsubir n;\nsubir 100;\n"
    assert _analyze(source) == []


# --- Ámbitos ---


def test_valid_sample_program_is_clean() -> None:
    source = (
        "ascensor A pisos 10;\n"
        "ir_a 5;\n"
        "abrir;\n"
        "esperar 3 segundos;\n"
        "cerrar;\n"
        "subir 2;\n"
        "abrir;\n"
    )
    assert _analyze(source) == []


def test_variable_out_of_scope() -> None:
    source = "si verdadero {\n    var dato : numero = 1;\n}\nimprimir dato;"
    errors = _analyze(source)
    assert len(errors) == 1
    assert errors[0].description == "la variable 'dato' no ha sido declarada"


def test_inner_scope_can_shadow() -> None:
    source = "var x : numero = 1;\nsi verdadero {\n    var x : numero = 2;\n}"
    assert _analyze(source) == []


def test_for_loop_variable_is_scoped() -> None:
    source = (
        "ascensor A pisos 10;\n"
        "para i desde 0 hasta 3 {\n"
        "    imprimir i;\n"
        "}\n"
        "imprimir i;\n"
    )
    errors = _analyze(source)
    assert len(errors) == 1
    assert errors[0].description == "la variable 'i' no ha sido declarada"


# --- Política de estado y casos adicionales ---


def test_floors_with_variable_count_is_untracked() -> None:
    # 'pisos n' no es constante: rango desconocido, sin error de positividad.
    source = "var n : numero = 5;\nascensor A pisos n;\nir_a 3;"
    assert _analyze(source) == []


def test_goto_reestablishes_known_floor() -> None:
    # Un 'ir_a' absoluto restablece el piso conocido tras un valor no constante.
    source = "ascensor A pisos 5;\nvar n : numero = 2;\nsubir n;\nir_a 4;\nsubir 5;\n"
    errors = _analyze(source)
    assert len(errors) == 1
    expected = "desde el piso 4 no se puede subir 5 pisos: excede el rango (0..5)"
    assert errors[0].description == expected


def test_movement_inside_branch_is_checked() -> None:
    source = "ascensor A pisos 5;\nir_a 3;\nsi 1 < 2 {\n    subir 10;\n}"
    errors = _analyze(source)
    assert len(errors) == 1
    assert "excede el rango" in errors[0].description


def test_door_open_in_both_branches_flags_move() -> None:
    source = (
        "ascensor A pisos 10;\n"
        "si 1 < 2 {\n    abrir;\n} sino {\n    abrir;\n}\n"
        "subir 1;\n"
    )
    errors = _analyze(source)
    assert any("puerta abierta" in error.description for error in errors)


def test_boundary_floors_are_allowed() -> None:
    # Llegar exactamente a 0 o al máximo es válido.
    assert _analyze("ascensor A pisos 5;\nir_a 5;\nbajar 5;\nir_a 0;") == []


def test_one_past_max_is_flagged() -> None:
    errors = _analyze("ascensor A pisos 5;\nir_a 6;")
    assert len(errors) == 1
    assert "excede el rango" in errors[0].description


def test_arg_type_and_open_door_errors_together() -> None:
    errors = _analyze("ascensor A pisos 10;\nabrir;\nsubir verdadero;")
    descriptions = " ".join(error.description for error in errors)
    assert "debe ser de tipo 'numero'" in descriptions
    assert "puerta abierta" in descriptions


def test_for_bound_must_be_numeric() -> None:
    errors = _analyze("para i desde verdadero hasta 3 {\n}")
    assert any("'para'" in error.description for error in errors)


def test_nested_scope_resolves_outer_variable() -> None:
    source = "var x : numero = 1;\nsi 1 < 2 {\n    x = 2;\n    imprimir x;\n}"
    assert _analyze(source) == []


# --- Estado del ascensor (unidad) ---


def test_state_join_differing_floors_is_unknown() -> None:
    first = ElevatorState()
    first.declare(10)
    first.set_floor(3)
    second = first.copy()
    second.set_floor(5)
    assert ElevatorState.join(first, second).floor is UNKNOWN


def test_state_join_equal_floors_stays_known() -> None:
    first = ElevatorState()
    first.declare(10)
    first.set_floor(4)
    assert ElevatorState.join(first, first.copy()).floor == 4


def test_state_join_differing_doors_is_unknown() -> None:
    first = ElevatorState()
    first.declare(10)
    second = first.copy()
    second.open_door()
    assert ElevatorState.join(first, second).door is Door.UNKNOWN
