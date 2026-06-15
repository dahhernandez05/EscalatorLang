"""Tipos de error y su recolección para las tres fases de análisis.

Una clase base arma el mensaje posicionado y formateado; cada subclase solo fija
su fase. ``ErrorCollector`` acumula los diagnósticos para que una fase pueda
reportar todos los problemas que encuentra en lugar de detenerse en el primero.
"""

from __future__ import annotations

from elevator_lang.messages import Phase, error_header


class ElevatorLangError(Exception):
    """Clase base de los errores de análisis con posición (línea y columna)."""

    def __init__(self, phase: Phase, line: int, column: int, description: str) -> None:
        self.phase = phase
        self.line = line
        self.column = column
        self.description = description
        super().__init__(self._render())

    def _render(self) -> str:
        return f"{error_header(self.phase, self.line, self.column)}: {self.description}"


class LexicalError(ElevatorLangError):
    """Error detectado durante el análisis léxico."""

    def __init__(self, line: int, column: int, description: str) -> None:
        super().__init__(Phase.LEXICAL, line, column, description)


class SyntacticError(ElevatorLangError):
    """Error detectado durante el análisis sintáctico."""

    def __init__(self, line: int, column: int, description: str) -> None:
        super().__init__(Phase.SYNTACTIC, line, column, description)


class SemanticError(ElevatorLangError):
    """Error detectado durante el análisis semántico."""

    def __init__(self, line: int, column: int, description: str) -> None:
        super().__init__(Phase.SEMANTIC, line, column, description)


class ErrorCollector:
    """Acumula errores para que cada fase los reporte todos juntos."""

    def __init__(self) -> None:
        self._errors: list[ElevatorLangError] = []

    def add(self, error: ElevatorLangError) -> None:
        self._errors.append(error)

    @property
    def errors(self) -> list[ElevatorLangError]:
        return list(self._errors)

    def has_errors(self) -> bool:
        return bool(self._errors)
