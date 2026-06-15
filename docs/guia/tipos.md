# Tipos y variables

ElevatorLang es un lenguaje con **tipado estático**: cada variable se declara con
un tipo fijo y el analizador comprueba que los valores que le asignas son
compatibles con él. Esta página describe los tres tipos disponibles, cómo se
escriben sus literales y cómo se declaran, inicializan y asignan las variables.

## Los tres tipos

El lenguaje tiene exactamente tres tipos. Sus nombres son palabras reservadas y se
escriben en minúsculas.

| Tipo | Palabra reservada | Valores | Ejemplo de literal |
|------|-------------------|---------|--------------------|
| Número | `numero` | enteros o decimales | `5`, `0`, `19.95` |
| Booleano | `booleano` | `verdadero` o `falso` | `verdadero` |
| Texto | `texto` | cadenas entre comillas dobles | `"hola"` |

### numero

El tipo `numero` cubre tanto los enteros como los decimales: no hay dos tipos
numéricos distintos. Un literal numérico es una secuencia de dígitos que,
opcionalmente, lleva una parte decimal introducida por un punto.

```elevator
var pisos_totales : numero = 10;
var tarifa : numero = 19.95;
```

!!! note "Números negativos"
    No existe un literal negativo: un valor como `-3` se forma aplicando el
    operador unario `-` a un literal. Lo mismo ocurre con `-` en medio de una
    expresión. Consulta [Expresiones](expresiones.md) para ver los operadores y su
    precedencia.

### booleano

El tipo `booleano` solo tiene dos valores, escritos con las palabras reservadas
`verdadero` y `falso`.

```elevator
var es_express : booleano = verdadero;
var en_pausa : booleano = falso;
```

Los valores booleanos son los que producen las comparaciones (`==`, `!=`, `<`,
`>`, `<=`, `>=`) y los operadores lógicos (`y`, `o`, `no`), y son el único tipo
admitido en las condiciones de `si`, `mientras` y similares.

### texto

El tipo `texto` representa una cadena de caracteres delimitada por comillas
dobles. Dentro de una cadena puedes usar **secuencias de escape**:

| Escape | Significado |
|--------|-------------|
| `\n` | salto de línea |
| `\t` | tabulación |
| `\"` | comilla doble literal |
| `\\` | barra invertida literal |

```elevator
var mensaje : texto = "Subiendo\tal piso objetivo\n";
var cita : texto = "Dijo \"hola\" y entró";
```

!!! warning "Cadenas y escapes"
    Una cadena no puede contener un salto de línea sin escapar ni quedar sin
    cerrar: ambos casos son **errores léxicos** (`cadena de texto sin cerrar`).
    Una secuencia de escape que no sea una de las cuatro de la tabla también es un
    error léxico (`secuencia de escape inválida '\x'`). Las reglas completas de
    los errores se detallan en
    [Errores](../referencia/errores.md).

## Declaración de variables

Una variable se declara con la palabra reservada `var`, su nombre, dos puntos, su
tipo y, opcionalmente, un inicializador `= expr`. La declaración termina en `;`.

```elevator
var x : numero = 5;
```

El inicializador es **opcional**. También puedes declarar una variable sin darle
un valor inicial:

```elevator
var contador : numero;
```

!!! warning "Usar una variable sin valor es un error semántico"
    Una variable declarada sin inicializador no tiene valor todavía. Si la
    **usas** (la lees en una expresión, la imprimes, etc.) antes de asignarle un
    valor, el analizador lo reporta:

    ```elevator
    ascensor torre pisos 5;
    var x : numero;
    imprimir x;
    ```

    ```text
    Error semántico [línea 3, columna 10]: la variable 'x' se usa antes de asignarle un valor
    ```

    Para usarla sin problemas, asígnale antes un valor (ver más abajo).

### Una sola declaración por ámbito

No puedes declarar dos veces la misma variable en el mismo ámbito. Hacerlo es un
error de redeclaración:

```elevator
ascensor torre pisos 5;
var x : numero = 0;
var x : texto = "hola";
```

```text
Error semántico [línea 3, columna 1]: la variable 'x' ya fue declarada en este ámbito
```

!!! tip "Ámbitos anidados"
    La restricción es *por ámbito*: un bloque, un `si`, un `mientras` o un `para`
    introducen un ámbito anidado donde sí puedes declarar un nombre que ya exista
    fuera. Las reglas de visibilidad y ámbitos se explican en
    [Control de flujo](control.md) y en las
    [reglas semánticas](../referencia/semantica.md).

## Asignación

Para cambiar el valor de una variable ya declarada se usa una sentencia de
asignación: el nombre, `=`, la expresión y `;`.

```elevator
contador = 0;
contador = contador + 1;
```

Asignar a una variable que no existe es un error semántico. Por ejemplo,
`destino = 5;` (sin haber declarado antes `destino`) produce:

```text
Error semántico [línea 1, columna 1]: la variable 'destino' no ha sido declarada
```

La asignación también es la forma de dar valor a una variable que se declaró sin
inicializador, evitando el error de "usar antes de asignar":

```elevator
var aviso : texto;
aviso = "Puerta abierta";
imprimir aviso;
```

## Reglas de tipos

El tipo de una variable se fija en su declaración y no cambia. Tanto el
inicializador como las asignaciones posteriores deben producir un valor del
**mismo tipo** que la variable; de lo contrario, el analizador reporta un error de
incompatibilidad de tipos.

```elevator
ascensor torre pisos 5;
var x : numero = 0;
x = verdadero;
```

```text
Error semántico [línea 3, columna 1]: no se puede asignar un valor de tipo 'booleano' a la variable 'x' de tipo 'numero'
```

La misma comprobación se aplica al inicializador de la declaración:

```elevator
ascensor torre pisos 5;
var activo : booleano = 3;
```

```text
Error semántico [línea 2, columna 1]: no se puede asignar un valor de tipo 'numero' a la variable 'activo' de tipo 'booleano'
```

!!! note "El tipo de una expresión"
    El tipo del lado derecho lo determinan los literales, las variables y los
    operadores que intervienen. Por ejemplo, una comparación siempre produce un
    `booleano`, y una suma de dos `numero` produce un `numero`. Los operadores
    también exigen tipos concretos en sus operandos, y mezclar tipos incompatibles
    (como `numero` y `texto`) es un error. Esas reglas se desarrollan en
    [Expresiones](expresiones.md) y en las
    [reglas semánticas](../referencia/semantica.md).

## Ejemplo completo

El siguiente programa declara variables de los tres tipos, las usa, las reasigna y
se analiza sin errores:

```elevator
ascensor torre pisos 10;

var piso_objetivo : numero = 5;
var es_express : booleano = verdadero;
var mensaje : texto = "Subiendo\tal piso objetivo\n";

// Declarada sin valor; se le asigna antes de usarla.
var contador : numero;
contador = 0;

piso_objetivo = piso_objetivo + 1;
es_express = piso_objetivo > 3 y no falso;

imprimir mensaje;
imprimir es_express;
imprimir contador;
```

```text
Análisis correcto: no se encontraron errores.
```
