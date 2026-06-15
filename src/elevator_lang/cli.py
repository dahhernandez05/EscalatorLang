"""Punto de entrada de línea de comandos del analizador de ElevatorLang.

La orquestación completa de las tres fases (leer un archivo `.asc` y ejecutar los
análisis léxico, sintáctico y semántico) se implementa en la Fase 4. Este módulo
solo provee el cableado del comando de consola.
"""

from __future__ import annotations


def main() -> int:
    """Ejecuta el analizador desde la línea de comandos.

    Returns:
        Código de salida del proceso (0 si la ejecución fue correcta).
    """
    print("elevator-lang: la CLI se implementa en la Fase 4.")
    return 0
