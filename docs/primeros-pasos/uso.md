# Uso del analizador

Una vez [instalado](instalacion.md) el proyecto, ya puedes analizar programas de
ElevatorLang. Esta página explica cómo invocar el analizador desde la línea de
comandos, qué significan sus códigos de salida y cómo interpretar lo que imprime
sobre los tres programas de ejemplo.

Los programas de ElevatorLang se guardan en archivos con la extensión **`.asc`**.
El analizador **no ejecuta** el programa ni genera código: lo lee, lo valida en
las fases léxica, sintáctica y semántica, y reporta los errores que encuentre con
su posición exacta (línea y columna).

## Analizar un archivo

Hay dos formas equivalentes de lanzar el analizador sobre un archivo `.asc`:

```bash
# Como módulo de Python:
uv run python -m elevator_lang <archivo.asc>

# O mediante el comando instalado (hace exactamente lo mismo):
uv run elevator-lang <archivo.asc>
```

Ambas reciben un único argumento: la ruta del archivo `.asc` que quieres
analizar. Por ejemplo:

```bash
uv run elevator-lang examples/prueba_valida.asc
```

Si el análisis es correcto, verás:

```text
Análisis correcto: no se encontraron errores.
```

Si hay errores, el analizador imprime cada uno en su propia línea y termina con
un resumen del total. El [formato de cada línea de error](../referencia/errores.md)
es siempre el mismo: tipo de error, posición y descripción.

!!! tip "¿`python -m elevator_lang` o `elevator-lang`?"
    Las dos invocaciones son intercambiables. El comando `elevator-lang` se
    instala junto con el paquete al ejecutar `uv sync`; `python -m elevator_lang`
    es útil si prefieres no depender de que el comando esté en el `PATH`.

## Códigos de salida

El analizador termina con un código de salida que resume el resultado. Esto es
útil para encadenarlo en scripts o en una canalización de integración continua.

| Código | Significado |
|:------:|-------------|
| `0` | Análisis correcto: no se encontró ningún error. |
| `1` | Se encontraron errores de análisis (léxicos, sintácticos o semánticos). |
| `2` | No se pudo leer el archivo, o el comando se usó de forma incorrecta. |

Puedes consultar el código de salida del último comando con `echo $?`:

```bash
uv run elevator-lang examples/prueba_valida.asc
echo $?   # imprime 0
```

!!! note "El código 2 no es un error del programa analizado"
    El código `2` indica un problema con la **invocación**, no con el código
    ElevatorLang: por ejemplo, que la ruta no exista o no se pueda leer. En ese
    caso el mensaje se imprime por la salida de error estándar (`stderr`):

    ```bash
    uv run elevator-lang examples/no_existe.asc
    ```

    ```text
    error: no se pudo leer 'examples/no_existe.asc': [Errno 2] No such file or directory: 'examples/no_existe.asc'
    ```

## El análisis se detiene en la primera fase con errores

El analizador trabaja en tres fases que se ejecutan **en orden**: primero la
**léxica**, luego la **sintáctica** y por último la **semántica**. Cada fase
necesita la salida correcta de la anterior, así que el análisis **se detiene en
la primera fase que encuentra errores** y solo reporta los de esa fase.

```text
léxica  ──▶  sintáctica  ──▶  semántica
  │             │                │
  └─ si falla, no se ejecutan las fases posteriores
```

Las consecuencias prácticas de este *phase-gating* son:

- Si el archivo tiene un error léxico (por ejemplo, un carácter que no pertenece
  al lenguaje), **no** verás errores sintácticos ni semánticos: primero hay que
  arreglar lo léxico.
- Si pasa la fase léxica pero falla la sintáctica (por ejemplo, falta un `;`),
  **no** se ejecuta el análisis semántico: no tiene sentido razonar sobre tipos
  o reglas del ascensor si el programa todavía no está bien formado.
- Solo cuando las fases léxica y sintáctica son correctas se ejecuta la
  comprobación semántica (variables, tipos y las reglas del dominio del
  ascensor).

!!! warning "Arregla los errores en orden"
    Como cada ejecución solo muestra los errores de **una** fase, conviene
    corregir lo que reporte y volver a analizar. Es normal que, tras arreglar un
    error sintáctico, una nueva ejecución revele errores semánticos que antes
    quedaban ocultos.

## Los tres programas de ejemplo

La carpeta `examples/` contiene tres programas pensados para mostrar cada uno de
los resultados posibles. A continuación se reproduce la salida real de cada uno.

### Programa válido

`examples/prueba_valida.asc` es correcto en las tres fases: declara un ascensor,
usa variables, expresiones, control de flujo y comandos del ascensor sin violar
ninguna regla.

```bash
uv run elevator-lang examples/prueba_valida.asc
```

```text
Análisis correcto: no se encontraron errores.
```

Código de salida: `0`.

### Error sintáctico

`examples/prueba_error_sintactico.asc` omite el `;` al final de la declaración
del ascensor. El parser espera un `;` y, en su lugar, encuentra la siguiente
palabra clave (`ir_a`).

```bash
uv run elevator-lang examples/prueba_error_sintactico.asc
```

```text
Error sintáctico [línea 6, columna 1]: se esperaba ';', se encontró 'ir_a'

Se encontró 1 error.
```

Código de salida: `1`. Como el programa no supera la fase sintáctica, el
análisis semántico **no llega a ejecutarse**.

### Error semántico

`examples/prueba_error_semantico.asc` es sintácticamente correcto, pero viola una
regla del dominio: el ascensor tiene 5 pisos (rango `0..5`) y, desde el piso 3,
`subir 10` se saldría del rango.

```bash
uv run elevator-lang examples/prueba_error_semantico.asc
```

```text
Error semántico [línea 8, columna 1]: desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)

Se encontró 1 error.
```

Código de salida: `1`. Aquí el programa **sí** superó las fases léxica y
sintáctica; el error aparece en la fase semántica.

!!! example "Pruébalo tú mismo"
    Ejecuta los tres ejemplos seguidos para ver los tres resultados:

    ```bash
    uv run elevator-lang examples/prueba_valida.asc
    uv run elevator-lang examples/prueba_error_sintactico.asc
    uv run elevator-lang examples/prueba_error_semantico.asc
    ```

## Siguientes pasos

- Consulta la [galería de ejemplos](../ejemplos.md) para ver más programas
  comentados.
- Revisa el [formato de los errores](../referencia/errores.md) para entender en
  detalle cada línea de diagnóstico.
