"""Resaltador de sintaxis de ElevatorLang para la documentación (MkDocs).

Define un lexer de Pygments para los bloques de código de ElevatorLang del sitio
de documentación. Se registra mediante un *entry point* ``pygments.lexers`` (ver
``pyproject.toml``), de modo que los bloques marcados con ` ```elevator ` se
colorean al construir el sitio. No forma parte del analizador en sí; solo se usa
para la documentación, por eso ``pygments`` es una dependencia de desarrollo.
"""

from __future__ import annotations

from pygments.lexer import RegexLexer, words
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Whitespace,
)

# Categorías de palabras reservadas (separadas para colorearlas distinto).
_DECLARATION = ("var", "ascensor")
_TYPES = ("numero", "booleano", "texto")
_CONTROL = ("si", "sino", "mientras", "para", "desde", "hasta", "imprimir")
_COMMANDS = ("subir", "bajar", "ir_a", "abrir", "cerrar", "esperar", "pisos", "segundos")
_CONSTANTS = ("verdadero", "falso")
_LOGICAL = ("y", "o", "no")


class ElevatorLangLexer(RegexLexer):
    """Lexer de Pygments para el DSL ElevatorLang."""

    name = "ElevatorLang"
    aliases = ["elevatorlang", "elevator"]  # noqa: RUF012
    filenames = ["*.asc"]  # noqa: RUF012

    tokens = {  # noqa: RUF012
        "root": [
            (r"\s+", Whitespace),
            (r"//[^\n]*", Comment.Single),
            (r"/\*", Comment.Multiline, "comment"),
            (r'"', String, "string"),
            (r"\d+\.\d+", Number.Float),
            (r"\d+", Number.Integer),
            (words(_DECLARATION, suffix=r"\b"), Keyword.Declaration),
            (words(_TYPES, suffix=r"\b"), Keyword.Type),
            (words(_CONSTANTS, suffix=r"\b"), Keyword.Constant),
            (words(_CONTROL, suffix=r"\b"), Keyword),
            (words(_COMMANDS, suffix=r"\b"), Name.Builtin),
            (words(_LOGICAL, suffix=r"\b"), Operator.Word),
            (r"==|!=|<=|>=|[-+*/<>=]", Operator),
            (r"[(){};:]", Punctuation),
            (r"[a-zA-Z_]\w*", Name),
        ],
        "comment": [
            (r"[^*]+", Comment.Multiline),
            (r"\*/", Comment.Multiline, "#pop"),
            (r"\*", Comment.Multiline),
        ],
        "string": [
            (r'\\[nt"\\]', String.Escape),
            (r'[^"\\\n]+', String),
            (r'"', String, "#pop"),
        ],
    }
