# Formato de errores

ElevatorLang no genera código: su trabajo es **leer, validar y reportar
errores** con su **posición exacta**. Esta página describe el formato posicionado
que comparten las tres fases del análisis (léxica, sintáctica y semántica), cómo
se **recolectan** los errores dentro de una fase y el **encadenamiento entre
fases** (*phase-gating*) que decide cuál de ellas llega a ejecutarse.

!!! note "Relación con las otras referencias"
    Aquí se documenta la **forma** de los mensajes y su numeración. El catálogo de
    símbolos que producen las posiciones está en la [referencia de
    tokens](tokens.md); la gramática que define los errores sintácticos, en la
    [gramática EBNF](gramatica.md); y el significado de cada diagnóstico
    semántico, en las [reglas semánticas](semantica.md).

## El formato posicionado

Todos los diagnósticos siguen un mismo encabezado, seguido de una descripción:

```text
Error <fase> [línea L, columna C]: <descripción>
```

Donde:

- **`<fase>`** es una de tres palabras: `léxico`, `sintáctico` o `semántico`.
- **`L`** es el número de **línea** (empezando en 1) donde se detecta el problema.
- **`C`** es el número de **columna** (empezando en 1) dentro de esa línea.
- **`<descripción>`** es el texto del problema concreto, en español.

El encabezado lo arma una única función, de modo que el formato es idéntico en
las tres fases; solo cambian la palabra de la fase y la descripción. Las líneas y
las columnas se cuentan **desde 1**.

!!! tip "La columna apunta al inicio del problema"
    La columna señala el comienzo del token o del carácter conflictivo, no el
    final de la línea. Esto hace que el cursor del error apunte al sitio exacto
    donde empezar a corregir.

## Un ejemplo de cada fase

A continuación, un programa mínimo que dispara cada tipo de error, con la salida
real del analizador.

### Error léxico

El léxico falla cuando encuentra un carácter que no forma parte del alfabeto del
lenguaje, una cadena de texto sin cerrar, un comentario de bloque sin cerrar o
una secuencia de escape inválida. Aquí, un carácter inesperado `@`:

```elevator
ascensor edificio pisos 10;
var x : numero = 5 @ 3;
```

```text
Error léxico [línea 2, columna 20]: carácter inesperado '@'
```

La columna `20` apunta al propio `@` en la segunda línea.

### Error sintáctico

El sintáctico falla cuando los tokens son válidos pero su **orden** no encaja con
la gramática. Su descripción siempre tiene la forma `se esperaba X, se encontró
Y`. Aquí falta el `;` que cierra la declaración de la variable:

```elevator
ascensor edificio pisos 10;

var destino : numero = 5
ir_a 5;
```

```text
Error sintáctico [línea 4, columna 1]: se esperaba ';', se encontró 'ir_a'
```

El analizador esperaba el punto y coma; al no encontrarlo, el siguiente token que
ve es `ir_a` (en la línea 4, columna 1), y eso es lo que reporta.

### Error semántico

El semántico falla cuando el programa está bien formado pero **viola una regla de
significado** (tipos, variables, o las reglas del dominio del ascensor). Aquí, un
movimiento que saca al ascensor de su rango de pisos:

```elevator
ascensor edificio pisos 5;

ir_a 3;
subir 10;
```

```text
Error semántico [línea 4, columna 1]: desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)
```

!!! warning "Cuando todo está bien"
    Si el programa supera las tres fases, el analizador no imprime ningún error,
    sino el mensaje `Análisis correcto: no se encontraron errores.` y termina con
    código `0`.

## Recolección de errores dentro de una fase

Dentro de una misma fase, el análisis **no se detiene en el primer error**: sigue
adelante y **recolecta todos** los problemas que encuentra, para reportarlos
juntos. Así, una sola ejecución puede corregir varios fallos a la vez.

Por ejemplo, dos caracteres inesperados en líneas distintas producen **dos**
errores léxicos:

```elevator
ascensor edificio pisos 10;
var x : numero = @ 3;
var y : numero = $ 4;
```

```text
Error léxico [línea 2, columna 18]: carácter inesperado '@'
Error léxico [línea 3, columna 18]: carácter inesperado '$'

Se encontraron 2 errores.
```

Lo mismo ocurre en la fase semántica; dos variables sin declarar dan dos
diagnósticos independientes:

```elevator
ascensor edificio pisos 5;
imprimir a;
imprimir b;
```

```text
Error semántico [línea 2, columna 10]: la variable 'a' no ha sido declarada
Error semántico [línea 3, columna 10]: la variable 'b' no ha sido declarada

Se encontraron 2 errores.
```

!!! note "Sin diagnósticos duplicados"
    El recolector descarta los errores **idénticos en la misma posición** (misma
    fase, línea, columna y descripción). Esto evita cascadas de mensajes
    repetidos cuando varias reglas anidadas fallan exactamente en el mismo punto.

Al final, el analizador resume el total: `Se encontró 1 error.` o `Se encontraron
N errores.` según corresponda.

## Encadenamiento entre fases (*phase-gating*)

Aunque dentro de una fase se recolectan todos los errores, **el análisis se
detiene en la primera fase que falla**. Las fases se ejecutan en orden —léxica,
luego sintáctica, luego semántica— y cada una necesita la salida correcta de la
anterior:

1. Se ejecuta el **léxico**. Si produce errores, se reportan y el análisis
   termina ahí: no se intenta parsear.
2. Si el léxico está limpio, se ejecuta el **sintáctico**. Si produce errores,
   se reportan y el análisis termina: no se hace análisis semántico.
3. Si el sintáctico está limpio, se ejecuta el **semántico** y se reportan sus
   errores (si los hay).

La consecuencia práctica es que **nunca verás errores de dos fases distintas en
la misma ejecución**. Por ejemplo, este programa tiene a la vez un error
sintáctico (falta el `;` tras la declaración del ascensor) y un error semántico
(ir al piso 20 excede el rango `0..5`):

```elevator
ascensor edificio pisos 5

ir_a 20;
```

Pero solo se reporta el sintáctico, porque el semántico nunca llega a
ejecutarse:

```text
Error sintáctico [línea 3, columna 1]: se esperaba ';', se encontró 'ir_a'
```

!!! tip "Corrige de arriba hacia abajo"
    Por el *phase-gating*, conviene corregir primero los errores léxicos, luego
    los sintácticos y, por último, los semánticos. Cada vez que limpias una fase,
    la siguiente queda al descubierto y puede aparecer con más diagnósticos.

## Códigos de salida

El analizador comunica el resultado también mediante su **código de salida**, útil
para integrarlo en scripts y herramientas automáticas:

| Código | Significado |
|:------:|-------------|
| `0` | Análisis correcto: no se encontró ningún error en las tres fases. |
| `1` | Se encontraron errores de análisis (léxicos, sintácticos o semánticos). |
| `2` | No se pudo leer el archivo, o el uso del comando fue incorrecto. |

El código `1` corresponde a cualquier error **dentro del programa** (sin importar
la fase). El código `2` es distinto: indica un problema **antes** de analizar,
como un archivo que no existe o no se puede leer. En ese caso el mensaje sale por
la salida de error estándar:

```text
error: no se pudo leer 'no_existe.asc': [Errno 2] No such file or directory: 'no_existe.asc'
```

!!! note "Cómo se invoca"
    Para más detalles sobre cómo ejecutar el analizador y leer su salida, consulta
    la página de [uso](../primeros-pasos/uso.md).
