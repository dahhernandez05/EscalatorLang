"""Analizador léxico de ElevatorLang.

El lexer convierte el texto fuente en una lista de tokens, omitiendo los espacios
en blanco y los comentarios, y registrando la línea y la columna (base 1) de cada
token. La entrada inválida se reporta como ``LexicalError`` recolectados para que
el escaneo pueda continuar.
"""

from __future__ import annotations

from elevator_lang import messages
from elevator_lang.errors import ElevatorLangError, ErrorCollector, LexicalError
from elevator_lang.tokens import KEYWORDS, Token, TokenType

# Caracteres que se omiten entre tokens.
_WHITESPACE: frozenset[str] = frozenset({" ", "\t", "\r", "\n"})

# Tokens de un solo carácter sin variante más larga.
_SINGLE_CHAR_TOKENS: dict[str, TokenType] = {
    "(": TokenType.PAREN_IZQ,
    ")": TokenType.PAREN_DER,
    "{": TokenType.LLAVE_IZQ,
    "}": TokenType.LLAVE_DER,
    ";": TokenType.PUNTO_COMA,
    ":": TokenType.DOS_PUNTOS,
    "+": TokenType.MAS,
    "-": TokenType.MENOS,
    "*": TokenType.POR,
}

# Operadores que cambian de significado cuando los sigue '='.
# Mapa: carácter inicial -> (sin '=', con '=').
_EQUAL_SUFFIX_TOKENS: dict[str, tuple[TokenType, TokenType]] = {
    "=": (TokenType.ASIGNAR, TokenType.IGUAL),
    "<": (TokenType.MENOR, TokenType.MENOR_IGUAL),
    ">": (TokenType.MAYOR, TokenType.MAYOR_IGUAL),
}

# Secuencias de escape reconocidas: carácter tras '\' -> carácter decodificado.
_ESCAPES: dict[str, str] = {
    "n": "\n",
    "t": "\t",
    '"': '"',
    "\\": "\\",
}


def _is_digit(character: str) -> bool:
    """Indica si el carácter es un dígito decimal."""
    return "0" <= character <= "9"


def _is_alpha(character: str) -> bool:
    """Indica si el carácter es una letra ASCII o un guion bajo."""
    return ("a" <= character <= "z") or ("A" <= character <= "Z") or character == "_"


def _is_alphanumeric(character: str) -> bool:
    """Indica si el carácter es una letra ASCII, un dígito o un guion bajo."""
    return _is_alpha(character) or _is_digit(character)


class Lexer:
    """Escanea el texto fuente de ElevatorLang y produce tokens."""

    def __init__(self, source: str) -> None:
        self._source = source
        self._tokens: list[Token] = []
        self._collector = ErrorCollector()
        self._start = 0
        self._current = 0
        self._line = 1
        self._column = 1
        self._token_line = 1
        self._token_column = 1

    @property
    def errors(self) -> list[ElevatorLangError]:
        """Errores léxicos recolectados durante el escaneo."""
        return self._collector.errors

    def scan_tokens(self) -> list[Token]:
        """Escanea todo el código y devuelve los tokens, terminando en EOF."""
        while not self._at_end():
            self._start = self._current
            self._token_line = self._line
            self._token_column = self._column
            self._scan_token()
        self._tokens.append(Token(TokenType.EOF, "", self._line, self._column))
        return self._tokens

    # --- Escaneo ---

    def _scan_token(self) -> None:
        character = self._advance()
        if character in _WHITESPACE:
            return
        if character in _SINGLE_CHAR_TOKENS:
            self._add_token(_SINGLE_CHAR_TOKENS[character])
            return
        if character in _EQUAL_SUFFIX_TOKENS:
            without_equal, with_equal = _EQUAL_SUFFIX_TOKENS[character]
            self._add_token(with_equal if self._match("=") else without_equal)
            return
        if character == "/":
            self._slash()
            return
        if character == "!":
            self._bang()
            return
        if character == '"':
            self._string()
            return
        if _is_digit(character):
            self._number()
            return
        if _is_alpha(character):
            self._identifier()
            return
        self._add_error(messages.unexpected_character(character))

    def _slash(self) -> None:
        # '/' inicia un comentario de línea, uno de bloque, o es división.
        if self._match("/"):
            self._line_comment()
        elif self._match("*"):
            self._block_comment()
        else:
            self._add_token(TokenType.ENTRE)

    def _bang(self) -> None:
        # '!' solo es válido como parte de '!='; suelto es un error.
        if self._match("="):
            self._add_token(TokenType.DISTINTO)
        else:
            self._add_error(messages.unexpected_character("!"))

    def _line_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _block_comment(self) -> None:
        while not self._at_end():
            if self._peek() == "*" and self._peek_next() == "/":
                self._advance()  # consume '*'
                self._advance()  # consume '/'
                return
            self._advance()
        self._add_error(messages.unterminated_block_comment())

    def _string(self) -> None:
        characters: list[str] = []
        while not self._at_end() and self._peek() != '"' and self._peek() != "\n":
            if self._peek() == "\\":
                self._advance()  # consume la barra invertida
                if self._at_end():
                    break
                characters.append(self._decode_escape(self._advance()))
            else:
                characters.append(self._advance())
        if self._at_end() or self._peek() != '"':
            self._add_error(messages.unterminated_string())
            return
        self._advance()  # comilla de cierre
        self._add_token(TokenType.TEXTO_LITERAL, "".join(characters))

    def _decode_escape(self, character: str) -> str:
        decoded = _ESCAPES.get(character)
        if decoded is None:
            self._add_error(messages.invalid_escape(character))
            return character
        return decoded

    def _number(self) -> None:
        while not self._at_end() and _is_digit(self._peek()):
            self._advance()
        is_decimal = False
        if self._peek() == "." and _is_digit(self._peek_next()):
            is_decimal = True
            self._advance()  # consume el '.'
            while not self._at_end() and _is_digit(self._peek()):
                self._advance()
        lexeme = self._source[self._start : self._current]
        value: int | float = float(lexeme) if is_decimal else int(lexeme)
        self._add_token(TokenType.NUMERO_LITERAL, value)

    def _identifier(self) -> None:
        while not self._at_end() and _is_alphanumeric(self._peek()):
            self._advance()
        text = self._source[self._start : self._current]
        self._add_token(KEYWORDS.get(text, TokenType.IDENTIFICADOR))

    # --- Auxiliares de caracteres ---

    def _advance(self) -> str:
        character = self._source[self._current]
        self._current += 1
        if character == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        return character

    def _match(self, expected: str) -> bool:
        if self._at_end() or self._source[self._current] != expected:
            return False
        self._advance()
        return True

    def _peek(self) -> str:
        if self._at_end():
            return ""
        return self._source[self._current]

    def _peek_next(self) -> str:
        next_index = self._current + 1
        if next_index >= len(self._source):
            return ""
        return self._source[next_index]

    def _at_end(self) -> bool:
        return self._current >= len(self._source)

    # --- Emisores ---

    def _add_token(
        self, token_type: TokenType, value: int | float | str | None = None
    ) -> None:
        lexeme = self._source[self._start : self._current]
        token = Token(token_type, lexeme, self._token_line, self._token_column, value)
        self._tokens.append(token)

    def _add_error(self, description: str) -> None:
        error = LexicalError(self._token_line, self._token_column, description)
        self._collector.add(error)
