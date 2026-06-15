"""Texto de los diagnósticos de ElevatorLang.

Todas las cadenas de los mensajes viven aquí, y solo aquí, para que la redacción
sea consistente y nunca quede incrustada en la lógica del analizador. Los nombres
de función están en inglés (convención del proyecto); el texto que devuelven está
en castellano y con tildes, como exige la especificación. El formato exacto del
encabezado es ``Error <fase> [línea L, columna C]: <descripción>``.
"""

from __future__ import annotations

from enum import Enum


class Phase(Enum):
    """Fase de análisis a la que pertenece un diagnóstico.

    El valor de cada miembro es la palabra que aparece en el encabezado del error.
    """

    LEXICAL = "léxico"
    SYNTACTIC = "sintáctico"
    SEMANTIC = "semántico"


def error_header(phase: Phase, line: int, column: int) -> str:
    """Devuelve el encabezado, p. ej. ``Error léxico [línea 4, columna 12]``."""
    return f"Error {phase.value} [línea {line}, columna {column}]"


# --- Descripciones de la fase léxica ---


def unexpected_character(character: str) -> str:
    return f"carácter inesperado '{character}'"


def unterminated_string() -> str:
    return "cadena de texto sin cerrar"


def unterminated_block_comment() -> str:
    return "comentario de bloque sin cerrar"


def invalid_escape(character: str) -> str:
    return f"secuencia de escape inválida '\\{character}'"


# --- Descripciones de la fase sintáctica ---

# Fragmentos reutilizables para los mensajes "se esperaba ...".
EXPECTED_IDENTIFIER = "un identificador"
EXPECTED_EXPRESSION = "una expresión"
EXPECTED_STATEMENT = "una sentencia"
EXPECTED_TYPE = "un tipo (numero, booleano o texto)"
END_OF_FILE = "fin de archivo"


def quoted(text: str) -> str:
    """Encierra un símbolo entre comillas simples para los mensajes."""
    return f"'{text}'"


def syntax_expected(expected: str, found: str) -> str:
    """Mensaje sintáctico que indica qué se esperaba y qué se encontró."""
    return f"se esperaba {expected}, se encontró {found}"


# --- Descripciones de la fase semántica ---


def undeclared_variable(name: str) -> str:
    return f"la variable '{name}' no ha sido declarada"


def redeclared_variable(name: str) -> str:
    return f"la variable '{name}' ya fue declarada en este ámbito"


def use_before_assignment(name: str) -> str:
    return f"la variable '{name}' se usa antes de asignarle un valor"


def assignment_type_mismatch(value_type: str, name: str, var_type: str) -> str:
    return (
        f"no se puede asignar un valor de tipo '{value_type}' a la variable "
        f"'{name}' de tipo '{var_type}'"
    )


def binary_type_error(left: str, right: str) -> str:
    return f"operación inválida entre un valor '{left}' y uno '{right}'"


def operand_type_error(expected: str) -> str:
    return f"los operandos de esta operación deben ser de tipo '{expected}'"


def unary_type_error(expected: str, actual: str) -> str:
    return f"el operador unario requiere un valor '{expected}', no '{actual}'"


def condition_not_boolean(actual: str) -> str:
    return f"la condición debe ser de tipo 'booleano', no '{actual}'"


def bound_not_numeric(actual: str) -> str:
    return f"los límites de 'para' deben ser de tipo 'numero', no '{actual}'"


def command_arg_not_numeric(command: str, actual: str) -> str:
    return f"el argumento de '{command}' debe ser de tipo 'numero', no '{actual}'"


def floors_not_numeric(actual: str) -> str:
    return f"el número de pisos debe ser de tipo 'numero', no '{actual}'"


def floors_not_positive() -> str:
    return "el número de pisos debe ser un entero positivo"


def no_ascensor() -> str:
    return "no hay ningún ascensor declarado"


def ascensor_already_declared() -> str:
    return "el ascensor ya fue declarado"


def goto_out_of_range(target: int, max_floor: int) -> str:
    return f"no se puede ir al piso {target}: excede el rango (0..{max_floor})"


def move_out_of_range(floor: int, verb: str, delta: int, max_floor: int) -> str:
    return (
        f"desde el piso {floor} no se puede {verb} {delta} pisos: "
        f"excede el rango (0..{max_floor})"
    )


def move_not_positive(command: str) -> str:
    return f"el movimiento de '{command}' debe ser positivo"


def wait_not_positive() -> str:
    return "el tiempo de espera debe ser positivo"


def move_with_open_door() -> str:
    return "no se puede mover el ascensor con la puerta abierta; falta 'cerrar'"
