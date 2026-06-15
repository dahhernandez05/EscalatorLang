"""Pruebas de extremo a extremo de la CLI (Fase 4).

Ejecutan los tres programas de ejemplo a través de ``analyze_source`` y ``main``,
comprobando la fase del error, el mensaje exacto y los códigos de salida.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from elevator_lang.cli import analyze_source, main
from elevator_lang.messages import Phase

_EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def _read(name: str) -> str:
    return (_EXAMPLES / name).read_text(encoding="utf-8")


# --- analyze_source: las tres fases ---


def test_valid_example_has_no_errors() -> None:
    assert analyze_source(_read("prueba_valida.asc")) == []


def test_syntactic_example_reports_syntactic_error() -> None:
    errors = analyze_source(_read("prueba_error_sintactico.asc"))
    assert errors
    assert all(error.phase is Phase.SYNTACTIC for error in errors)
    assert errors[0].description == "se esperaba ';', se encontró 'ir_a'"


def test_semantic_example_reports_spec_message() -> None:
    errors = analyze_source(_read("prueba_error_semantico.asc"))
    assert errors
    assert all(error.phase is Phase.SEMANTIC for error in errors)
    expected = "desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)"
    assert errors[0].description == expected


def test_lexical_error_stops_before_parsing() -> None:
    errors = analyze_source("ascensor A pisos @;")
    assert errors
    assert all(error.phase is Phase.LEXICAL for error in errors)


# --- main: salida y códigos de retorno ---


def test_main_valid_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = main([str(_EXAMPLES / "prueba_valida.asc")])
    captured = capsys.readouterr()
    assert code == 0
    assert "correcto" in captured.out


def test_main_semantic_error_returns_one(capsys: pytest.CaptureFixture[str]) -> None:
    code = main([str(_EXAMPLES / "prueba_error_semantico.asc")])
    captured = capsys.readouterr()
    assert code == 1
    assert "Error semántico" in captured.out
    assert "excede el rango (0..5)" in captured.out


def test_main_missing_file_returns_two(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["no_existe_xyz.asc"])
    captured = capsys.readouterr()
    assert code == 2
    assert "no se pudo leer" in captured.err


def test_main_plural_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source_file = tmp_path / "dos_errores.asc"
    source_file.write_text("ascensor A pisos @;\nimprimir #;\n", encoding="utf-8")
    code = main([str(source_file)])
    captured = capsys.readouterr()
    assert code == 1
    assert "Se encontraron 2 errores." in captured.out


def test_main_directory_argument_returns_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main([str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "no se pudo leer" in captured.err


def test_main_success_message_is_exact(capsys: pytest.CaptureFixture[str]) -> None:
    main([str(_EXAMPLES / "prueba_valida.asc")])
    captured = capsys.readouterr()
    assert "Análisis correcto: no se encontraron errores." in captured.out
