"""Modelo del estado abstracto del ascensor para las reglas del dominio.

Implementa la política «exacto en línea recta, desconocido tras ramas
ambiguas»: el piso se sigue con exactitud mientras los argumentos sean
constantes; cuando deja de poder determinarse, pasa a ``DESCONOCIDO`` y las
comprobaciones de rango se posponen hasta que un ``ir_a`` absoluto lo restablece.
"""

from __future__ import annotations

from enum import Enum


class Door(Enum):
    """Estado de la puerta del ascensor."""

    CLOSED = "cerrada"
    OPEN = "abierta"
    UNKNOWN = "desconocida"


class _Unknown:
    """Marcador de piso desconocido (cima del retículo de seguimiento)."""

    def __repr__(self) -> str:
        return "DESCONOCIDO"


UNKNOWN = _Unknown()

type Floor = int | _Unknown


def _same_floor(first: Floor, second: Floor) -> bool:
    """Indica si dos pisos son el mismo valor conocido."""
    if isinstance(first, _Unknown) or isinstance(second, _Unknown):
        return False
    return first == second


class ElevatorState:
    """Estado abstracto del ascensor durante el análisis semántico."""

    def __init__(self) -> None:
        self._declared = False
        self._range_known = False
        self._max_floor = 0
        self._floor: Floor = 0
        self._door = Door.CLOSED

    @property
    def declared(self) -> bool:
        return self._declared

    @property
    def range_known(self) -> bool:
        return self._range_known

    @property
    def max_floor(self) -> int:
        return self._max_floor

    @property
    def floor(self) -> Floor:
        return self._floor

    @property
    def door(self) -> Door:
        return self._door

    def declare(self, max_floor: int | None) -> None:
        """Registra el ascensor; ``None`` deja el rango como desconocido."""
        self._declared = True
        self._floor = 0
        self._door = Door.CLOSED
        if max_floor is None:
            self._range_known = False
            self._max_floor = 0
        else:
            self._range_known = True
            self._max_floor = max_floor

    def set_floor(self, floor: Floor) -> None:
        self._floor = floor

    def mark_floor_unknown(self) -> None:
        self._floor = UNKNOWN

    def open_door(self) -> None:
        self._door = Door.OPEN

    def close_door(self) -> None:
        self._door = Door.CLOSED

    def copy(self) -> ElevatorState:
        """Devuelve una copia independiente del estado."""
        clone = ElevatorState()
        clone._declared = self._declared
        clone._range_known = self._range_known
        clone._max_floor = self._max_floor
        clone._floor = self._floor
        clone._door = self._door
        return clone

    @staticmethod
    def join(first: ElevatorState, second: ElevatorState) -> ElevatorState:
        """Une dos estados de ramas: lo que difiere queda DESCONOCIDO."""
        merged = first.copy()
        if not _same_floor(first._floor, second._floor):
            merged._floor = UNKNOWN
        if first._door is not second._door:
            merged._door = Door.UNKNOWN
        merged._declared = first._declared and second._declared
        return merged
