"""Pruebas del analizador léxico (Fase 1).

Cubren el reconocimiento de cada clase de token, el descarte de comentarios, el
seguimiento de posiciones y los errores léxicos con su formato exacto.
"""

from __future__ import annotations

from elevator_lang.lexer import Lexer
from elevator_lang.tokens import KEYWORDS, TokenType


def _types(source: str) -> list[TokenType]:
    """Devuelve los tipos de token de ``source`` sin el EOF final."""
    tokens = Lexer(source).scan_tokens()
    return [token.type for token in tokens[:-1]]


# --- Tabla de palabras reservadas ---


def test_keywords_table_maps_reserved_words() -> None:
    assert KEYWORDS["ascensor"] is TokenType.ASCENSOR
    assert KEYWORDS["ir_a"] is TokenType.IR_A
    assert KEYWORDS["mientras"] is TokenType.MIENTRAS
    # El marcador de identificador no es una palabra reservada.
    assert "IDENTIFICADOR" not in KEYWORDS


# --- Identificadores y palabras reservadas ---


def test_keyword_and_identifier_are_distinguished() -> None:
    tokens = Lexer("ascensor casa").scan_tokens()
    assert [t.type for t in tokens] == [
        TokenType.ASCENSOR,
        TokenType.IDENTIFICADOR,
        TokenType.EOF,
    ]
    assert tokens[1].lexeme == "casa"


def test_boolean_keywords_are_recognized() -> None:
    assert _types("verdadero falso") == [TokenType.VERDADERO, TokenType.FALSO]


# --- Literales numéricos ---


def test_integer_literal_has_int_value() -> None:
    token = Lexer("42").scan_tokens()[0]
    assert token.type is TokenType.NUMERO_LITERAL
    assert token.value == 42
    assert isinstance(token.value, int)


def test_decimal_literal_has_float_value() -> None:
    token = Lexer("3.14").scan_tokens()[0]
    assert token.type is TokenType.NUMERO_LITERAL
    assert token.value == 3.14
    assert isinstance(token.value, float)


def test_trailing_dot_is_not_part_of_the_number() -> None:
    # "5." escanea el número 5 y deja el '.' como carácter inválido.
    lexer = Lexer("5.")
    tokens = lexer.scan_tokens()
    assert tokens[0].type is TokenType.NUMERO_LITERAL
    assert tokens[0].value == 5
    assert len(lexer.errors) == 1


# --- Literales de texto ---


def test_string_literal_decodes_escapes() -> None:
    token = Lexer(r'"a\nb\t\"c"').scan_tokens()[0]
    assert token.type is TokenType.TEXTO_LITERAL
    assert token.value == 'a\nb\t"c'


# --- Operadores y delimitadores ---


def test_operators_single_and_double_char() -> None:
    assert _types("== != <= >= < > = + - * /") == [
        TokenType.IGUAL,
        TokenType.DISTINTO,
        TokenType.MENOR_IGUAL,
        TokenType.MAYOR_IGUAL,
        TokenType.MENOR,
        TokenType.MAYOR,
        TokenType.ASIGNAR,
        TokenType.MAS,
        TokenType.MENOS,
        TokenType.POR,
        TokenType.ENTRE,
    ]


def test_delimiters() -> None:
    assert _types("(){};:") == [
        TokenType.PAREN_IZQ,
        TokenType.PAREN_DER,
        TokenType.LLAVE_IZQ,
        TokenType.LLAVE_DER,
        TokenType.PUNTO_COMA,
        TokenType.DOS_PUNTOS,
    ]


# --- Comentarios ---


def test_line_comment_is_skipped() -> None:
    assert _types("subir // baja\nabrir") == [TokenType.SUBIR, TokenType.ABRIR]


def test_block_comment_is_skipped() -> None:
    assert _types("subir /* esto\nse ignora */ abrir") == [
        TokenType.SUBIR,
        TokenType.ABRIR,
    ]


# --- Posiciones ---


def test_token_positions_are_one_based() -> None:
    tokens = Lexer("var\n  x").scan_tokens()
    assert (tokens[0].line, tokens[0].column) == (1, 1)
    assert (tokens[1].line, tokens[1].column) == (2, 3)


def test_last_token_is_eof() -> None:
    tokens = Lexer("abrir;").scan_tokens()
    assert tokens[-1].type is TokenType.EOF
    assert tokens[-1].lexeme == ""


# --- Errores léxicos ---


def test_unexpected_character_reports_position_and_message() -> None:
    lexer = Lexer("var x = @;")
    lexer.scan_tokens()
    assert len(lexer.errors) == 1
    error = lexer.errors[0]
    assert error.line == 1
    assert error.column == 9
    assert str(error) == "Error léxico [línea 1, columna 9]: carácter inesperado '@'"


def test_unterminated_string_is_reported() -> None:
    lexer = Lexer('imprimir "hola')
    lexer.scan_tokens()
    assert len(lexer.errors) == 1
    assert lexer.errors[0].description == "cadena de texto sin cerrar"


def test_unterminated_block_comment_is_reported() -> None:
    lexer = Lexer("subir /* sin cierre")
    lexer.scan_tokens()
    assert len(lexer.errors) == 1
    assert lexer.errors[0].description == "comentario de bloque sin cerrar"


def test_invalid_escape_is_reported() -> None:
    lexer = Lexer(r'"mal\q"')
    lexer.scan_tokens()
    assert len(lexer.errors) == 1
    assert lexer.errors[0].description == "secuencia de escape inválida '\\q'"


def test_scanning_continues_after_errors() -> None:
    lexer = Lexer("@ # abrir")
    tokens = lexer.scan_tokens()
    assert len(lexer.errors) == 2
    assert any(token.type is TokenType.ABRIR for token in tokens)


# --- Programa de ejemplo válido ---


def test_valid_sample_program_has_no_lexical_errors() -> None:
    source = (
        "ascensor A pisos 10;\n"
        "ir_a 5;\n"
        "abrir;\n"
        "esperar 3 segundos;\n"
        "cerrar;\n"
        "subir 2;\n"
        "abrir;\n"
    )
    lexer = Lexer(source)
    lexer.scan_tokens()
    assert lexer.errors == []


# --- Casos límite ---


def test_number_and_identifier_adjacency() -> None:
    assert _types("5subir") == [TokenType.NUMERO_LITERAL, TokenType.SUBIR]


def test_whole_valued_decimal_stays_float() -> None:
    token = Lexer("3.0").scan_tokens()[0]
    assert token.value == 3.0
    assert isinstance(token.value, float)


def test_keyword_prefix_is_an_identifier() -> None:
    # Munch máximo: 'subiendo' no es la palabra reservada 'subir'.
    assert _types("subiendo verdaderox") == [
        TokenType.IDENTIFICADOR,
        TokenType.IDENTIFICADOR,
    ]


def test_lone_bang_is_unexpected_character() -> None:
    lexer = Lexer("subir ! 2")
    lexer.scan_tokens()
    assert len(lexer.errors) == 1
    assert lexer.errors[0].column == 7
    assert lexer.errors[0].description == "carácter inesperado '!'"


def test_invalid_escape_still_emits_token() -> None:
    lexer = Lexer(r'"a\qb"')
    tokens = lexer.scan_tokens()
    assert len(lexer.errors) == 1
    assert tokens[0].type is TokenType.TEXTO_LITERAL
    assert tokens[0].value == "aqb"


def test_block_comment_does_not_nest() -> None:
    # El primer '*/' cierra el comentario; el '*/' sobrante se re-tokeniza.
    assert _types("/* a /* b */ c */") == [
        TokenType.IDENTIFICADOR,
        TokenType.POR,
        TokenType.ENTRE,
    ]


def test_column_counts_tab_as_one() -> None:
    # Convención: cada carácter que no sea salto de línea avanza una columna.
    tokens = Lexer("\tabrir").scan_tokens()
    assert (tokens[0].line, tokens[0].column) == (1, 2)


def test_eof_position_after_final_newline() -> None:
    tokens = Lexer("abrir\n").scan_tokens()
    assert tokens[-1].type is TokenType.EOF
    assert (tokens[-1].line, tokens[-1].column) == (2, 1)
