"""Tabla de símbolos y ámbitos para el análisis semántico.

Cada ámbito (``Scope``) guarda los símbolos declarados en él y enlaza con su
ámbito padre, de modo que la resolución de nombres recorre la cadena de ámbitos
anidados.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from elevator_lang.tokens import TokenType


class SymbolType(Enum):
    """Tipo de un valor del dominio."""

    NUMERO = "numero"
    BOOLEANO = "booleano"
    TEXTO = "texto"


# Token de tipo -> tipo del dominio. Traduce la palabra reservada de una
# declaración al tipo semántico correspondiente.
_TYPE_BY_TOKEN: dict[TokenType, SymbolType] = {
    TokenType.NUMERO: SymbolType.NUMERO,
    TokenType.BOOLEANO: SymbolType.BOOLEANO,
    TokenType.TEXTO: SymbolType.TEXTO,
}


def symbol_type_for(token_type: TokenType) -> SymbolType:
    """Traduce la palabra reservada de un tipo a su ``SymbolType``."""
    return _TYPE_BY_TOKEN[token_type]


@dataclass
class Symbol:
    """Una variable declarada: su nombre, tipo, estado y posición."""

    name: str
    type: SymbolType
    initialized: bool
    line: int
    column: int


class Scope:
    """Ámbito léxico: símbolos propios y enlace al ámbito padre."""

    def __init__(self, parent: Scope | None = None) -> None:
        self._parent = parent
        self._symbols: dict[str, Symbol] = {}

    @property
    def parent(self) -> Scope | None:
        return self._parent

    def declare(self, symbol: Symbol) -> bool:
        """Declara un símbolo; devuelve ``False`` si ya existía en este ámbito."""
        if symbol.name in self._symbols:
            return False
        self._symbols[symbol.name] = symbol
        return True

    def resolve(self, name: str) -> Symbol | None:
        """Busca un símbolo en este ámbito y, si no está, en los ancestros."""
        scope: Scope | None = self
        while scope is not None:
            found = scope._symbols.get(name)
            if found is not None:
                return found
            scope = scope._parent
        return None
