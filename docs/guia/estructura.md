# Estructura de un programa

Un programa de ElevatorLang es, sencillamente, una **secuencia de sentencias**
que se ejecutan de arriba hacia abajo. No hay una función `main` ni un punto de
entrada especial: el archivo `.asc` se lee de principio a fin y cada sentencia se
analiza en orden.

```elevator
programa = { sentencia } ;
```

La convención habitual es declarar primero el ascensor, después las variables
que vaya a usar el programa y, a continuación, los comandos y las estructuras de
control que describen su comportamiento. No es una regla sintáctica estricta,
pero hace los programas mucho más legibles.

!!! note "Un solo ascensor"
    Un programa declara **un único ascensor**. Declararlo dos veces es un error
    semántico (`el ascensor ya fue declarado`), y mover el ascensor antes de
    declararlo también lo es (`no hay ningún ascensor declarado`).

## Tipos de sentencia

Estos son los ocho tipos de sentencia que reconoce el lenguaje. Cada uno se
explica en detalle en su página correspondiente; aquí solo se resume su forma.

### Declaración del ascensor

Define el ascensor y su rango de pisos. El número de pisos `N` establece el
rango válido `0..N`; el ascensor arranca en el **piso 0** con la **puerta
cerrada**.

```elevator
ascensor torre pisos 10;
```

Más detalles en [Comandos del ascensor](ascensor.md).

### Declaración de variable

Introduce una variable con un tipo (`numero`, `booleano` o `texto`) y un
inicializador **opcional**.

```elevator
var destino : numero = 5;   // con inicializador
var contador : numero;      // sin inicializador
```

Más detalles en [Tipos y variables](tipos.md).

### Asignación

Asigna un nuevo valor a una variable **ya declarada**. El tipo del valor debe
coincidir con el tipo de la variable.

```elevator
destino = destino + 1;
```

### Comando del ascensor

Las acciones del dominio: moverse, abrir y cerrar la puerta, y esperar.

```elevator
ir_a 5;
subir 2;
bajar 3;
abrir;
cerrar;
esperar 5 segundos;
```

Más detalles en [Comandos del ascensor](ascensor.md).

### Impresión

Evalúa una expresión y la imprime.

```elevator
imprimir "Subiendo al piso objetivo";
imprimir destino;
```

### Condicional (`si` / `sino`)

Ejecuta un bloque si la condición es verdadera. El bloque `sino` es opcional. La
condición debe ser de tipo `booleano`.

```elevator
si destino > 3 {
    subir 2;
} sino {
    bajar 1;
}
```

Más detalles en [Control de flujo](control.md).

### Bucles (`mientras` / `para`)

El bucle `mientras` repite un bloque mientras se cumpla una condición booleana;
el bucle `para` cuenta de un valor inicial hasta uno final.

```elevator
mientras n > 0 {
    imprimir n;
    n = n - 1;
}

para i desde 1 hasta 3 {
    imprimir i;
}
```

Más detalles en [Control de flujo](control.md).

### Bloque

Un grupo de sentencias entre llaves `{ ... }`. Un bloque **introduce un ámbito
anidado**: las variables declaradas dentro solo existen dentro de él.

```elevator
{
    var temporal : numero = 0;
    imprimir temporal;
}
```

!!! tip "El punto y coma"
    Las sentencias simples (declaración, asignación, comandos, `imprimir`)
    terminan en `;`. Las que contienen un bloque (`si`, `mientras`, `para` y el
    propio bloque `{ ... }`) **no** llevan `;` después de la llave de cierre.

## Comentarios

ElevatorLang admite dos clases de comentarios. El analizador léxico los descarta
por completo, así que no afectan al programa: sirven solo para documentarlo.

**Comentario de línea.** Empieza con `//` y llega hasta el final de la línea.

```elevator
// Esto es un comentario de línea.
ir_a 5;   // también puede ir al final de una línea con código
```

**Comentario de bloque.** Empieza con `/*` y termina en el primer `*/`. Puede
ocupar varias líneas.

```elevator
/* Este comentario
   ocupa varias líneas. */
```

!!! warning "Los comentarios de bloque no anidan"
    Un comentario de bloque termina en el **primer** `*/` que aparezca; no se
    pueden anidar unos dentro de otros.

## Un programa completo

El siguiente programa reúne todos los tipos de sentencia y ambos estilos de
comentario. Es válido en las tres fases del análisis (léxica, sintáctica y
semántica).

```elevator
// Declaración del ascensor: define el rango de pisos 0..10.
ascensor torre pisos 10;

/* Declaramos las variables que usará el programa.
   El inicializador "= expr" es opcional. */
var destino : numero = 5;
var saludo : texto = "Bienvenido al edificio";

// Asignación: reasignamos una variable ya declarada.
destino = destino + 1;

// Impresión de un valor.
imprimir saludo;

// Comandos del ascensor (código lineal: el piso se sigue con exactitud).
ir_a 5;
abrir;
esperar 3 segundos;
cerrar;

// Condicional con bloque "sino" opcional.
si destino > 3 {
    subir 2;
} sino {
    bajar 1;
}

// Bloque anidado: introduce un ámbito propio.
{
    var temporal : numero = 0;
    imprimir temporal;
}

// Bucle contado: la variable i vive dentro del bucle.
para i desde 1 hasta 3 {
    imprimir i;
}
```

Si guardas este programa en un archivo `.asc` y lo analizas, obtienes:

```text
Análisis correcto: no se encontraron errores.
```

## Y a continuación

- [Tipos y variables](tipos.md): los tipos `numero`, `booleano` y `texto`, y
  cómo se declaran y asignan las variables.
- [Expresiones y operadores](expresiones.md): los siete niveles de precedencia y
  cómo se combinan los operandos.
- [Control de flujo](control.md): `si` / `sino`, `mientras` y `para` en detalle.
- [Comandos del ascensor](ascensor.md): los comandos del dominio y las reglas
  que verifica el analizador.
