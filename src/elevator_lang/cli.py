"""Punto de entrada de línea de comandos del analizador de ElevatorLang.

Orquesta las tres fases sobre un archivo fuente ``.asc``: análisis léxico,
sintáctico y semántico. Reporta los errores de la primera fase que falle, con el
formato que exige la especificación, y devuelve un código de salida distinto de
cero si encuentra algún error.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from elevator_lang.errors import ElevatorLangError
from elevator_lang.lexer import Lexer
from elevator_lang.parser import Parser
from elevator_lang.semantic_analyzer import SemanticAnalyzer


def analyze_source(source: str) -> list[ElevatorLangError]:
    """Ejecuta las tres fases sobre ``source`` y devuelve los errores.

    Se detiene en la primera fase que reporte errores: cada fase necesita la
    salida correcta de la anterior, así que no es fiable continuar con una
    entrada ya inválida.
    """
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    if lexer.errors:
        return lexer.errors
    parser = Parser(tokens)
    program = parser.parse()
    if parser.errors:
        return parser.errors
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    return analyzer.errors


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada del comando ``elevator-lang``."""
    arg_parser = argparse.ArgumentParser(
        prog="elevator-lang",
        description="Analizador léxico, sintáctico y semántico de ElevatorLang.",
    )
    arg_parser.add_argument("archivo", help="archivo fuente .asc a analizar")
    args = arg_parser.parse_args(argv)

    path = Path(args.archivo)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"error: no se pudo leer '{args.archivo}': {error}", file=sys.stderr)
        return 2

    errors = analyze_source(source)
    if not errors:
        print("Análisis correcto: no se encontraron errores.")
        return 0
    for error in errors:
        print(error)
    if len(errors) == 1:
        print("\nSe encontró 1 error.")
    else:
        print(f"\nSe encontraron {len(errors)} errores.")
    return 1
