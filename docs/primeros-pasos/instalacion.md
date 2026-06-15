# Instalación

Esta página explica cómo dejar listo el entorno de **ElevatorLang** en tu
máquina: qué necesitas, cómo instalar el proyecto, cómo ejecutar las pruebas y
cómo construir esta documentación localmente.

## Requisitos

- **Python 3.12** o superior.
- **[uv](https://docs.astral.sh/uv/)** como gestor de paquetes y entorno.

!!! note "Sin dependencias en tiempo de ejecución"
    El analizador **no tiene dependencias en tiempo de ejecución**: funciona solo
    con la biblioteca estándar de Python. Las herramientas de desarrollo
    (`pytest`, `ruff`, `ty`) las declara el proyecto y las gestiona `uv`, así que
    no necesitas instalarlas a mano.

Si aún no tienes `uv`, sigue las
[instrucciones oficiales de instalación](https://docs.astral.sh/uv/getting-started/installation/).
`uv` se encarga de crear el entorno virtual y de proporcionar la versión de
Python adecuada, por lo que normalmente no necesitas preparar nada más.

## Instalar el proyecto

Desde la raíz del repositorio, ejecuta:

```bash
uv sync
```

Esto crea el entorno virtual (`.venv/`) e instala el paquete en modo editable,
junto con las herramientas de desarrollo del grupo `dev`.

!!! tip "Comprueba que todo funciona"
    Tras `uv sync`, analiza uno de los programas de ejemplo para confirmar que
    la instalación es correcta:

    ```bash
    uv run python -m elevator_lang examples/prueba_valida.asc
    ```

    Deberías ver:

    ```text
    Análisis correcto: no se encontraron errores.
    ```

    Si quieres aprender a usar el analizador con tus propios archivos, continúa
    en [Uso del analizador](uso.md).

## Ejecutar las pruebas

El proyecto incluye una batería de pruebas con `pytest`. Para ejecutarla:

```bash
uv run pytest
```

`uv` resuelve automáticamente las dependencias de desarrollo, así que no hace
falta instalar `pytest` por separado: basta con haber ejecutado `uv sync`.

## Construir la documentación localmente

Esta documentación se genera con
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/), que pertenece al
grupo de dependencias `docs`. Para instalarlo y previsualizar el sitio:

```bash
uv sync --group docs
uv run mkdocs serve
```

El comando `mkdocs serve` levanta un servidor local (por defecto en
<http://127.0.0.1:8000/>) que recarga la página automáticamente cada vez que
editas un archivo de `docs/`.

!!! note "Generar el sitio estático"
    Si en lugar de previsualizar quieres generar los archivos HTML del sitio,
    usa `uv run mkdocs build`; el resultado se escribe en la carpeta `site/`.

## Siguiente paso

Con el entorno listo, pasa a [Uso del analizador](uso.md) para aprender a
analizar tus propios programas `.asc`.
