"""Punto de entrada de linea de comandos del analizador de ElevatorLang.

La orquestacion completa de las tres fases (leer un archivo `.asc` y
ejecutar los analisis lexico, sintactico y semantico) se implementa en la
Fase 4. Este modulo solo provee el cableado del comando de consola.
"""

from __future__ import annotations


def main() -> int:
    """Ejecuta el analizador desde la linea de comandos.

    Returns:
        Codigo de salida del proceso (0 si la ejecucion fue correcta).
    """
    print("elevator-lang: la CLI se implementa en la Fase 4.")
    return 0
