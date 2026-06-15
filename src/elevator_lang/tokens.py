"""Modelo de tokens de ElevatorLang.

Este módulo es la única fuente de verdad para los tipos de token (``TokenType``)
y para la tabla de palabras reservadas (``KEYWORDS``). Ningún otro módulo debe
escribir directamente el texto de las palabras reservadas ni las categorías de
token; impórtalos desde aquí.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Todos los tipos de token que el analizador léxico puede producir.

    Para palabras reservadas, operadores y delimitadores, el valor del miembro
    es el texto exacto del código fuente. Para identificadores, literales y fin
    de archivo, el valor es un nombre simbólico (esos tokens guardan su texto
    concreto en ``Token.lexeme``).
    """

    # --- Palabras reservadas del dominio ---
    ASCENSOR = "ascensor"
    PISOS = "pisos"
    SUBIR = "subir"
    BAJAR = "bajar"
    IR_A = "ir_a"
    ABRIR = "abrir"
    CERRAR = "cerrar"
    ESPERAR = "esperar"
    SEGUNDOS = "segundos"

    # --- Palabras reservadas del núcleo ---
    VAR = "var"
    NUMERO = "numero"
    BOOLEANO = "booleano"
    TEXTO = "texto"
    SI = "si"
    SINO = "sino"
    MIENTRAS = "mientras"
    PARA = "para"
    DESDE = "desde"
    HASTA = "hasta"
    IMPRIMIR = "imprimir"
    VERDADERO = "verdadero"
    FALSO = "falso"
    Y = "y"
    # El nombre de un solo carácter refleja la palabra reservada "o" (disyunción).
    O = "o"  # noqa: E741
    NO = "no"

    # --- Identificadores y literales ---
    IDENTIFICADOR = "IDENTIFICADOR"
    NUMERO_LITERAL = "NUMERO_LITERAL"
    TEXTO_LITERAL = "TEXTO_LITERAL"

    # --- Operadores ---
    MAS = "+"
    MENOS = "-"
    POR = "*"
    ENTRE = "/"
    ASIGNAR = "="
    IGUAL = "=="
    DISTINTO = "!="
    MENOR = "<"
    MAYOR = ">"
    MENOR_IGUAL = "<="
    MAYOR_IGUAL = ">="

    # --- Delimitadores ---
    PAREN_IZQ = "("
    PAREN_DER = ")"
    LLAVE_IZQ = "{"
    LLAVE_DER = "}"
    PUNTO_COMA = ";"
    DOS_PUNTOS = ":"

    # --- Fin de la entrada ---
    EOF = "EOF"


# Tipos de token que son palabras reservadas. Se listan una sola vez aquí para
# que el texto de cada palabra reservada viva solo en el valor del enum (DRY):
# KEYWORDS se deriva de esta lista.
_KEYWORD_TYPES: tuple[TokenType, ...] = (
    TokenType.ASCENSOR,
    TokenType.PISOS,
    TokenType.SUBIR,
    TokenType.BAJAR,
    TokenType.IR_A,
    TokenType.ABRIR,
    TokenType.CERRAR,
    TokenType.ESPERAR,
    TokenType.SEGUNDOS,
    TokenType.VAR,
    TokenType.NUMERO,
    TokenType.BOOLEANO,
    TokenType.TEXTO,
    TokenType.SI,
    TokenType.SINO,
    TokenType.MIENTRAS,
    TokenType.PARA,
    TokenType.DESDE,
    TokenType.HASTA,
    TokenType.IMPRIMIR,
    TokenType.VERDADERO,
    TokenType.FALSO,
    TokenType.Y,
    TokenType.O,
    TokenType.NO,
)

# Texto de palabra reservada -> tipo de token. Lo usa el lexer para distinguir
# las palabras reservadas de los identificadores.
KEYWORDS: dict[str, TokenType] = {
    token_type.value: token_type for token_type in _KEYWORD_TYPES
}


@dataclass(frozen=True)
class Token:
    """Una unidad léxica junto con su posición en el código fuente.

    Atributos:
        type: El tipo de token.
        lexeme: El texto exacto del que se escaneó el token.
        line: Línea (base 1) donde inicia el token.
        column: Columna (base 1) donde inicia el token.
        value: Valor literal decodificado para ``NUMERO_LITERAL`` (int/float) y
            ``TEXTO_LITERAL`` (str); ``None`` para cualquier otro tipo de token.
    """

    type: TokenType
    lexeme: str
    line: int
    column: int
    value: int | float | str | None = None
