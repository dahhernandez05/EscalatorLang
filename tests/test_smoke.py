"""Prueba de humo del paquete.

Verifica que el paquete es importable y expone su versión. Cada fase del
analizador se prueba en su módulo de pruebas correspondiente.
"""

from __future__ import annotations

import elevator_lang


def test_package_exposes_version() -> None:
    assert elevator_lang.__version__ == "0.1.0"
