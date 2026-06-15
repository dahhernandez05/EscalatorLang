"""Pruebas de humo del esqueleto del proyecto (Fase 0).

Verifican que el paquete es importable y que el cableado del comando de
consola responde. Las pruebas de cada fase del analizador se anaden en sus
respectivas fases.
"""

from __future__ import annotations

import elevator_lang
from elevator_lang.cli import main


def test_package_exposes_version() -> None:
    assert elevator_lang.__version__ == "0.1.0"


def test_cli_main_returns_success() -> None:
    assert main() == 0
