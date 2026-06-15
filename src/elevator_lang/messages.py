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
