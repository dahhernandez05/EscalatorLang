# Control de flujo

ElevatorLang ofrece tres estructuras de control: el condicional `si`/`sino`, el
bucle `mientras` y el bucle contado `para`. Las tres usan un **bloque** `{ ... }`
como cuerpo, y cada bloque introduce un **ámbito anidado** para las variables.

Esta página explica la sintaxis de cada estructura, las comprobaciones
semánticas que aplica el analizador y cómo se resuelven los nombres entre
ámbitos. Las reglas de tipos que se citan aquí (condición booleana, límites
numéricos, ocultamiento de variables) se detallan en la
[referencia de reglas semánticas](../referencia/semantica.md).

## Condicional: `si` / `sino`

```
si CONDICIÓN {
    ... // se ejecuta si la condición es verdadera
} sino {
    ... // se ejecuta si la condición es falsa
}
```

La rama `sino` es **opcional**: puedes escribir solo `si CONDICIÓN { ... }`.
Tanto la rama `si` como la rama `sino` son siempre **bloques** con llaves; no
existe la forma de una sola sentencia sin llaves.

La **condición debe ser de tipo `booleano`**. Una expresión numérica o de texto
en la condición es un error semántico:

```text
Error semántico [línea 5, columna 4]: la condición debe ser de tipo 'booleano', no 'numero'
```

!!! example "Condicional con las dos ramas"
    ```
    ascensor torre pisos 10;

    var destino : numero = 5;

    ir_a 4;

    si destino > 3 {
        subir 2;
    } sino {
        bajar 1;
    }
    ```

La condición puede ser un literal booleano, una variable de tipo `booleano`, una
comparación (`destino > 3`) o cualquier combinación con los operadores lógicos
`y`, `o` y `no`. Consulta [Expresiones](expresiones.md) para los detalles de
precedencia.

!!! example "Condicional sin `sino`"
    ```
    ascensor torre pisos 10;

    var activo : booleano = verdadero;

    si activo {
        ir_a 4;
        abrir;
        cerrar;
    }
    ```

## Bucle: `mientras`

```
mientras CONDICIÓN {
    ... // se repite mientras la condición sea verdadera
}
```

Como en el condicional, la **condición debe ser de tipo `booleano`**. El cuerpo
es un bloque con su propio ámbito.

!!! example "Bucle `mientras`"
    ```
    ascensor torre pisos 10;

    var n : numero = 0;

    mientras n < 3 {
        imprimir n;
        n = n + 1;
    }
    ```

!!! note "El analizador no ejecuta el bucle"
    ElevatorLang **valida**, no ejecuta. El analizador no calcula cuántas veces
    se repite el bucle ni si termina; solo comprueba que el programa es correcto
    en tipos y en las reglas del dominio. Por eso, tras un `mientras`, el piso
    del ascensor pasa a ser desconocido (ver más abajo).

## Bucle contado: `para`

```
para i desde A hasta B {
    ... // i recorre el rango definido por A y B
}
```

- La **variable del bucle** (`i` en el ejemplo) es de tipo `numero` y **vive solo
  dentro del bucle**: se declara automáticamente en el ámbito del cuerpo y deja
  de existir al cerrar la llave.
- Los **límites `A` y `B` deben ser de tipo `numero`**. Un límite de otro tipo es
  un error semántico:

  ```text
  Error semántico [línea 3, columna 14]: los límites de 'para' deben ser de tipo 'numero', no 'booleano'
  ```

!!! example "Bucle contado"
    ```
    ascensor torre pisos 10;

    para i desde 1 hasta 3 {
        imprimir i;
    }
    ```

Como la variable del bucle pertenece al ámbito del cuerpo, usarla **fuera** del
bucle es un error de variable no declarada:

```
ascensor torre pisos 10;

para i desde 1 hasta 3 {
    imprimir i;
}

imprimir i;   // error: 'i' no existe aquí
```

```text
Error semántico [línea 7, columna 10]: la variable 'i' no ha sido declarada
```

## Bloques y ámbitos anidados

Cada `{ ... }` —el cuerpo de un `si`, un `sino`, un `mientras`, un `para`, o un
bloque escrito por sí solo— abre un **ámbito anidado**. Las reglas de resolución
de nombres son:

- Una variable declarada **dentro** de un bloque **no existe fuera** de él.
- Una variable de un ámbito interno puede **ocultar** (hacer sombra a) una del
  ámbito externo con el mismo nombre, incluso si tiene otro tipo. Mientras dura
  el bloque, el nombre se refiere a la variable interna; al salir, vuelve a
  referirse a la externa.
- Declarar **dos veces** el mismo nombre en el **mismo** ámbito es un error:

  ```text
  Error semántico [línea 4, columna 1]: la variable 'x' ya fue declarada en este ámbito
  ```

!!! example "Una variable interna oculta a la externa"
    ```
    ascensor torre pisos 10;

    var x : numero = 1;
    imprimir x;          // usa la x externa (numero)

    si x > 0 {
        var x : booleano = verdadero;
        imprimir x;      // usa la x interna (booleano), que oculta a la externa
    }

    imprimir x;          // de nuevo la x externa (numero)
    ```

    Las dos declaraciones de `x` conviven sin conflicto porque están en ámbitos
    distintos: la primera en el ámbito del programa, la segunda en el ámbito del
    bloque `si`.

Si declaras una variable dentro de un bloque y la usas fuera, el analizador la
considera no declarada:

```
ascensor torre pisos 10;

si verdadero {
    var interna : numero = 1;
    imprimir interna;
}

imprimir interna;   // error: 'interna' solo existía dentro del bloque
```

```text
Error semántico [línea 8, columna 10]: la variable 'interna' no ha sido declarada
```

## Seguimiento del piso en ramas

El analizador sigue el piso actual del ascensor para comprobar la regla de rango
de pisos. La política es **«exacto en línea recta, desconocido tras ramas
ambiguas»**: mientras el código avanza de forma lineal con argumentos
constantes, el piso se conoce con exactitud; en cuanto interviene una estructura
de control cuyo efecto sobre el piso no puede determinarse, el piso pasa a ser
**desconocido** y las comprobaciones de rango se posponen, sin falsos positivos,
hasta que un `ir_a` con valor constante restablece una posición conocida.

!!! warning "Después de un `si`, `mientras` o `para`, el piso suele quedar desconocido"
    Cuando un `si` deja el ascensor en pisos distintos según la rama, o cuando un
    `mientras`/`para` lo mueve un número de veces que el analizador no calcula,
    el piso resultante es desconocido. Por eso este programa **no** produce un
    error de rango, aunque el bucle aparente salirse del rango: tras el bucle el
    piso es desconocido, y `ir_a 0` lo restablece dentro de rango.

    ```
    ascensor torre pisos 5;

    var n : numero = 0;

    mientras n < 10 {
        subir 1;
        n = n + 1;
    }

    ir_a 0;
    ```

Esta política, junto con las otras reglas del dominio (puerta cerrada para
moverse y movimiento positivo), se explica en detalle en
[Comandos del ascensor](ascensor.md).

## Resumen

| Estructura | Sintaxis | Comprobación principal |
|------------|----------|------------------------|
| Condicional | `si cond { } sino { }` (el `sino` es opcional) | `cond` debe ser `booleano` |
| Bucle | `mientras cond { }` | `cond` debe ser `booleano` |
| Bucle contado | `para i desde A hasta B { }` | `A` y `B` deben ser `numero`; `i` es `numero` y vive solo en el bucle |

Cada bloque abre un ámbito anidado: lo declarado dentro no existe fuera, y un
nombre interno puede ocultar a uno externo. Consulta la
[referencia de reglas semánticas](../referencia/semantica.md) para la lista
completa de comprobaciones y sus mensajes exactos.
