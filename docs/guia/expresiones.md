# Expresiones y operadores

Una **expresión** es cualquier fragmento de código que produce un valor: un
literal, una variable, una operación entre valores o una agrupación con
paréntesis. Las expresiones aparecen en todas partes: en el inicializador de una
variable, en el lado derecho de una asignación, como condición de un `si` o un
`mientras`, como límites de un `para`, como argumento de los comandos del
ascensor y dentro de `imprimir`.

ElevatorLang ofrece operadores **aritméticos**, **relacionales**, de
**igualdad**, **lógicos** y dos operadores **unarios**. Cada categoría produce un
tipo concreto, y el [análisis semántico](../referencia/semantica.md) comprueba
que los operandos tengan el tipo adecuado.

## Categorías de operadores

### Aritméticos (`+ - * /`)

Operan sobre dos valores de tipo `numero` y producen un `numero`.

| Operador | Significado     |
| -------- | --------------- |
| `+`      | suma            |
| `-`      | resta           |
| `*`      | multiplicación  |
| `/`      | división        |

```
var total : numero = 2 + 3 * 4;     // 14
var medio : numero = 10 / 2;        // 5
var resto : numero = (8 - 3) * 2;   // 10
```

!!! warning "Solo entre números"
    Si alguno de los operandos no es `numero`, el analizador informa:

    ```text
    Error semántico [línea 1, columna 20]: los operandos deben ser de tipo 'numero', pero son 'numero' y 'texto'
    ```

### Relacionales (`< > <= >=`)

Comparan dos valores de tipo `numero` y producen un `booleano`.

| Operador | Significado       |
| -------- | ----------------- |
| `<`      | menor que         |
| `>`      | mayor que         |
| `<=`     | menor o igual que |
| `>=`     | mayor o igual que |

```
var alto : booleano = piso > 5;
var seguro : booleano = velocidad <= 10;
```

### Igualdad (`== !=`)

Comparan dos valores y producen un `booleano`. A diferencia de los operadores
relacionales, la igualdad admite cualquier tipo, pero **ambos operandos deben ser
del mismo tipo** entre sí.

| Operador | Significado |
| -------- | ----------- |
| `==`     | igual a     |
| `!=`     | distinto de |

```
var llego : booleano = piso == 0;
var distinto : booleano = nombre != "torre";
```

!!! warning "Mismo tipo a ambos lados"
    Comparar valores de tipos diferentes es un error:

    ```text
    Error semántico [línea 1, columna 22]: operación inválida entre un valor 'numero' y uno 'texto'
    ```

### Lógicos (`y o`)

Combinan dos valores de tipo `booleano` y producen un `booleano`.

| Operador | Significado          |
| -------- | -------------------- |
| `y`      | conjunción (AND)     |
| `o`      | disyunción (OR)      |

```
var en_rango : booleano = piso >= 0 y piso <= 10;
var movil : booleano = subiendo o bajando;
```

!!! warning "Solo entre booleanos"
    Si un operando no es `booleano`, el analizador informa:

    ```text
    Error semántico [línea 1, columna 30]: los operandos deben ser de tipo 'booleano', pero son 'booleano' y 'numero'
    ```

### Unarios (`-` y `no`)

Se aplican a un único operando, que va a su derecha.

| Operador | Operando esperado | Resultado  | Significado          |
| -------- | ----------------- | ---------- | -------------------- |
| `-`      | `numero`          | `numero`   | negación aritmética  |
| `no`     | `booleano`        | `booleano` | negación lógica      |

```
var bajo_cero : numero = -5;
var inverso : booleano = no abierto;
```

El unario `no` exige un operando `booleano` y el unario `-` un operando `numero`.
Usarlos sobre el tipo equivocado es un error:

```text
Error semántico [línea 1, columna 20]: el operador unario requiere un valor 'booleano', no 'numero'
```

!!! note "El operador unario es asociativo por la derecha"
    Como un unario puede aplicarse a otro unario, expresiones como `no no
    verdadero` o `--3` son válidas y se evalúan de derecha a izquierda.

## Tipo que produce cada categoría

| Categoría     | Operadores      | Tipo de los operandos | Tipo del resultado |
| ------------- | --------------- | --------------------- | ------------------ |
| Aritmética    | `+ - * /`       | `numero`              | `numero`           |
| Relacional    | `< > <= >=`     | `numero`              | `booleano`         |
| Igualdad      | `== !=`         | mismo tipo entre sí   | `booleano`         |
| Lógica        | `y o`           | `booleano`            | `booleano`         |
| Unario `-`    | `-`             | `numero`              | `numero`           |
| Unario `no`   | `no`            | `booleano`            | `booleano`         |

## Precedencia y asociatividad

Cuando una expresión combina varios operadores sin paréntesis, la **precedencia**
decide qué operación se agrupa primero: a mayor precedencia, más fuerte la
ligadura. ElevatorLang define **siete niveles**, de **menor a mayor** precedencia.

| Nivel | Operadores         | Categoría            | Asociatividad        |
| :---: | ------------------ | -------------------- | -------------------- |
| 1     | `o`                | lógico (OR)          | izquierda            |
| 2     | `y`                | lógico (AND)         | izquierda            |
| 3     | `== !=`            | igualdad             | izquierda            |
| 4     | `< > <= >=`        | relacional           | izquierda            |
| 5     | `+ -`              | aditiva              | izquierda            |
| 6     | `* /`              | multiplicativa       | izquierda            |
| 7     | `no` `-` (unario)  | unario               | derecha              |
|  —    | literal, variable, `( )` | primario       | —                    |

Todos los operadores **binarios** son **asociativos por la izquierda**: ante
operadores del mismo nivel, se agrupan de izquierda a derecha. El operador
**unario** es **asociativo por la derecha**.

!!! example "Cómo se agrupa una expresión"
    Las siguientes parejas son equivalentes; la columna derecha hace explícita la
    agrupación implícita:

    ```
    2 + 3 * 4            =>   2 + (3 * 4)            // * antes que +
    10 - 4 - 2          =>   (10 - 4) - 2           // - asociativo por la izquierda
    a > 0 y b > 0        =>   (a > 0) y (b > 0)      // relacional antes que y
    a o b y c            =>   a o (b y c)            // y antes que o
    no a y b             =>   (no a) y b             // unario antes que y
    ```

## Agrupación con paréntesis

Los paréntesis `( )` agrupan una subexpresión y la fuerzan a evaluarse primero,
por encima de cualquier precedencia. Son la forma de alterar el orden natural.

```
var sin_parentesis : numero = 2 + 3 * 4;   // 14
var con_parentesis : numero = (2 + 3) * 4; // 20
```

Una expresión entre paréntesis conserva el tipo de su contenido, de modo que
puedes anidarlos libremente:

```
var ok : booleano = no (piso == 0 o piso == 10);
```

## Ejemplos completos

!!! example "Expresiones válidas"
    ```
    var a : numero = 2 + 3 * 4;
    var b : numero = (2 + 3) * 4;
    var c : numero = -5 + 10 / 2;
    var d : booleano = a > b;
    var e : booleano = a == 14;
    var f : booleano = verdadero y no falso;
    var g : booleano = a > 0 o b < 0;
    var h : booleano = no (a == b);
    imprimir a;
    imprimir d;
    ```

    Al analizar este programa, el resultado es:

    ```text
    Análisis correcto: no se encontraron errores.
    ```

!!! tip "Dónde puedes usar expresiones"
    Cualquier lugar donde el lenguaje espera un valor admite una expresión
    completa, no solo un literal. Por ejemplo, el argumento de un comando del
    ascensor puede ser una expresión aritmética:

    ```
    ascensor torre pisos 10;
    var destino : numero = 2;
    ir_a destino + 3;
    ```

## Comprobaciones de tipos

El analizador verifica el tipo de cada operando y rechaza las combinaciones
inválidas. Estos son los mensajes que verás cuando una expresión no encaja:

- Operandos de tipo incorrecto en aritmética, relacional o lógica:
  `los operandos deben ser de tipo 'numero', pero son 'numero' y 'texto'`
- Igualdad entre tipos distintos:
  `operación inválida entre un valor 'numero' y uno 'texto'`
- Operador unario sobre el tipo equivocado:
  `el operador unario requiere un valor 'booleano', no 'numero'`

Consulta el catálogo completo en las
[reglas semánticas](../referencia/semantica.md) y el formato de los diagnósticos
en la [referencia de errores](../referencia/errores.md). Para repasar los tipos
del lenguaje, visita [Tipos](tipos.md); para ver dónde encajan las expresiones
dentro de las estructuras del lenguaje, [Estructuras de control](control.md).
