<p align="center">
  <img src="docs/assets/logo.png" alt="ElevatorLang" width="150">
</p>

# ElevatorLang

Analizador **léxico**, **sintáctico** y **semántico** de **ElevatorLang**, un
lenguaje de dominio específico (DSL) para programar el comportamiento de un
ascensor: subir, bajar, abrir y cerrar puertas, esperar e ir a un piso. El
analizador lee un programa, lo valida en las tres fases y reporta errores con su
posición exacta (línea y columna). Proyecto final de la asignatura Compiladores
(ficha 15).

> No genera código máquina: su objetivo es **leer, validar y reportar errores**
> significativos en las fases léxica, sintáctica y semántica.

## Requisitos

- **Python 3.12** o superior.
- **[uv](https://docs.astral.sh/uv/)** como gestor de paquetes y entorno.

El analizador no tiene dependencias en tiempo de ejecución (solo biblioteca
estándar). Las herramientas de desarrollo (`pytest`, `ruff`, `ty`) las gestiona
`uv`.

## Instalación

```bash
uv sync
```

Esto crea el entorno virtual e instala el paquete en modo editable.

## Uso

Los programas de ElevatorLang usan la extensión **`.asc`**. Para analizar un
archivo:

```bash
uv run python -m elevator_lang <archivo.asc>
# o, de forma equivalente, mediante el comando instalado:
uv run elevator-lang <archivo.asc>
```

**Códigos de salida:**

| Código | Significado |
|:------:|-------------|
| `0` | Análisis correcto: no se encontraron errores |
| `1` | Se encontraron errores de análisis (léxicos, sintácticos o semánticos) |
| `2` | No se pudo leer el archivo, o el uso del comando fue incorrecto |

El análisis se detiene en la **primera fase** que encuentra errores, ya que cada
fase necesita la salida correcta de la anterior.

## Programas de ejemplo

La carpeta `examples/` contiene los tres programas de prueba exigidos:

```bash
# Programa correcto en las tres fases -> salida correcta, código 0
uv run python -m elevator_lang examples/prueba_valida.asc

# Error sintáctico (falta un ';') -> código 1
uv run python -m elevator_lang examples/prueba_error_sintactico.asc

# Sintácticamente correcto, pero semánticamente inválido -> código 1
uv run python -m elevator_lang examples/prueba_error_semantico.asc
```

Salidas esperadas de los dos programas con error:

```text
Error sintáctico [línea 6, columna 1]: se esperaba ';', se encontró 'ir_a'

Error semántico [línea 8, columna 1]: desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)
```

## El lenguaje en breve

> La tabla completa de tokens, la gramática formal en EBNF y la explicación
> detallada de las reglas semánticas se encuentran en el documento técnico. La
> gramática formal también está disponible en
> [`docs/gramatica.ebnf`](docs/gramatica.ebnf).

**Palabras reservadas**

- Dominio del ascensor: `ascensor`, `pisos`, `subir`, `bajar`, `abrir`,
  `cerrar`, `esperar`, `ir_a`, `segundos`.
- Núcleo del lenguaje: `var`, `numero`, `booleano`, `texto`, `si`, `sino`,
  `mientras`, `para`, `desde`, `hasta`, `imprimir`, `verdadero`, `falso`,
  `y`, `o`, `no`.

**Tipos:** `numero` (entero o decimal), `booleano`, `texto`.

**Operadores:** aritméticos `+ - * /`, relacionales `< > <= >= == !=`,
lógicos `y o no` (siete niveles de precedencia).

**Comentarios:** de línea `// ...` y de bloque `/* ... */`.

**Programa de ejemplo:**

```
ascensor edificio pisos 10;

var destino : numero = 5;
imprimir "Yendo al piso objetivo";

ir_a 5;
abrir;
esperar 3 segundos;
cerrar;

si destino > 3 {
    subir 2;
} sino {
    bajar 1;
}
```

### Reglas del dominio que verifica el analizador

1. **Rango de pisos:** un movimiento que saque al ascensor del rango `0..N` es
   error (p. ej. `subir 10` desde el piso 3 con un ascensor de 5 pisos).
2. **Puerta cerrada para moverse:** no se puede mover el ascensor con la puerta
   abierta; hay que `cerrar` antes de volver a moverse.
3. **Movimiento positivo:** `subir` y `bajar` exigen una cantidad positiva
   (`subir -1;` es error; usa `bajar`).

Además de las reglas anteriores, el analizador detecta el uso de variables no
declaradas, redeclaraciones en el mismo ámbito, tipos incompatibles y el uso de
una variable antes de asignarle un valor.

## Formato de los errores

Todos los errores siguen el mismo formato posicionado:

```text
Error léxico     [línea L, columna C]: <descripción>
Error sintáctico [línea L, columna C]: se esperaba X, se encontró Y
Error semántico  [línea L, columna C]: <regla violada>
```

## Estructura del proyecto

```text
elevator_lang/
├── src/elevator_lang/
│   ├── tokens.py             # tipos de token y palabras reservadas
│   ├── lexer.py              # análisis léxico
│   ├── ast_nodes.py          # nodos del AST
│   ├── visitor.py            # patrón visitor
│   ├── parser.py             # análisis sintáctico (descendente recursivo)
│   ├── symbols.py            # tabla de símbolos y ámbitos
│   ├── elevator_state.py     # simulación del estado del ascensor
│   ├── semantic_analyzer.py  # análisis semántico
│   ├── errors.py             # jerarquía de errores
│   ├── messages.py           # textos de los diagnósticos
│   └── cli.py                # interfaz de línea de comandos
├── tests/                    # pruebas (pytest)
├── examples/                 # los tres programas de prueba (.asc)
└── docs/gramatica.ebnf       # gramática formal en EBNF
```

## Pruebas

```bash
uv run pytest
```

## Herramientas de desarrollo

- **[uv](https://docs.astral.sh/uv/)** — gestor de paquetes y entorno.
- **[ruff](https://docs.astral.sh/ruff/)** — formateador y linter (PEP 8).
- **[ty](https://github.com/astral-sh/ty)** — verificador estático de tipos.
- **[pytest](https://docs.pytest.org/)** — ejecución de pruebas.

```bash
uv run ruff format .      # formatear
uv run ruff check .       # lint
uv run ty check           # tipos
uv run pytest             # pruebas
```

## Licencia

[MIT](LICENSE) © 2026 dahhernandez05.
