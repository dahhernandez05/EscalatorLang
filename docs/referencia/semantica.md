# Reglas semánticas

El **análisis semántico** es la tercera y última fase del analizador. Solo se
ejecuta si las fases [léxica](tokens.md) y [sintáctica](gramatica.md) no
encontraron errores: cada fase necesita la salida correcta de la anterior, así
que el análisis se detiene en la **primera fase** que falla.

Mientras que la fase sintáctica comprueba que el programa tiene una *forma*
válida, la fase semántica comprueba que ese programa tiene *sentido*: que las
variables existen antes de usarse, que los tipos encajan y que el ascensor se
maneja respetando las reglas de su dominio.

!!! note "Formato de los errores"
    Todos los diagnósticos de esta fase tienen la forma exacta:

    ```text
    Error semántico [línea L, columna C]: <regla violada>
    ```

    Los errores se recolectan, así que un mismo análisis puede reportar varios.
    En esta página, cada regla se acompaña de un ejemplo que la viola y del
    **mensaje exacto** que produce el analizador.

---

## La tabla de símbolos y los ámbitos anidados

Para saber qué variables existen y de qué tipo son, el analizador mantiene una
**tabla de símbolos** organizada por **ámbitos** (en inglés, *scopes*). Cada
ámbito guarda los símbolos declarados en él y enlaza con su ámbito padre,
formando una cadena.

Cada símbolo registra el **nombre** de la variable, su **tipo** (`numero`,
`booleano` o `texto`), si ya ha sido **inicializada** y su posición en el código.

### Cómo se resuelven los nombres

Cuando se usa una variable, el analizador la busca primero en el ámbito actual y,
si no la encuentra, sube por la cadena de ámbitos padre hasta el ámbito global.
La primera coincidencia gana. Si llega al ámbito global sin encontrarla, la
variable no está declarada.

### Qué introduce un ámbito nuevo

Cada uno de estos crea un ámbito anidado, que desaparece al cerrarse:

- un **bloque** `{ ... }`;
- el cuerpo de un bucle `mientras`;
- un condicional `si` / `sino` (cada rama tiene su bloque);
- un bucle `para`, cuyo ámbito contiene además la **variable de control** (de
  tipo `numero`, visible solo dentro del bucle).

Una variable declarada dentro de un ámbito anidado **no es visible fuera de él**:

```elevator
ascensor torre pisos 5;
{
    var interna : numero = 1;
    imprimir interna;
}
imprimir interna;
```

```text
Error semántico [línea 6, columna 10]: la variable 'interna' no ha sido declarada
```

---

## Comprobaciones genéricas de variables y tipos

### Variable no declarada

Toda variable debe declararse (con `var`) antes de leerse o asignársele un valor.

```elevator
ascensor torre pisos 10;
imprimir x;
```

```text
Error semántico [línea 2, columna 10]: la variable 'x' no ha sido declarada
```

### Redeclaración en el mismo ámbito

No se puede declarar dos veces la misma variable **dentro del mismo ámbito**.
(Declararla de nuevo en un ámbito anidado sí es válido: la nueva oculta a la
anterior mientras dura ese ámbito.)

```elevator
ascensor torre pisos 10;
var x : numero = 1;
var x : numero = 2;
```

```text
Error semántico [línea 3, columna 1]: la variable 'x' ya fue declarada en este ámbito
```

### Uso antes de asignar un valor

El inicializador de `var` es opcional. Si declaras una variable **sin** valor, no
puedes leerla hasta haberle asignado uno con `=`.

```elevator
ascensor torre pisos 10;
var x : numero;
imprimir x;
```

```text
Error semántico [línea 3, columna 10]: la variable 'x' se usa antes de asignarle un valor
```

!!! tip
    Para evitar este error, da un valor inicial en la declaración
    (`var x : numero = 0;`) o asígnalo (`x = 0;`) antes del primer uso.

### Tipo incompatible en una asignación

El valor que se asigna —tanto en la declaración `var x : T = expr;` como en una
asignación `x = expr;`— debe coincidir con el tipo declarado de la variable.

```elevator
ascensor torre pisos 10;
var x : numero = verdadero;
```

```text
Error semántico [línea 2, columna 1]: no se puede asignar un valor de tipo 'booleano' a la variable 'x' de tipo 'numero'
```

### Operandos de tipo incorrecto

Los operadores tienen exigencias de tipo según su categoría. Consulta los
[operadores y su precedencia](../guia/expresiones.md) para el detalle de cada uno.

- **Aritméticos** (`+ - * /`) y **relacionales** (`< > <= >=`): ambos operandos
  deben ser `numero`.
- **Lógicos** (`y`, `o`): ambos operandos deben ser `booleano`.

```elevator
ascensor torre pisos 10;
var x : numero = 1 + "hola";
```

```text
Error semántico [línea 2, columna 20]: los operandos deben ser de tipo 'numero', pero son 'numero' y 'texto'
```

### Igualdad entre tipos distintos

Los operadores de igualdad (`==`, `!=`) admiten cualquier tipo, pero **ambos
lados deben ser del mismo tipo**.

```elevator
ascensor torre pisos 5;
var b : booleano = 1 == "x";
```

```text
Error semántico [línea 2, columna 22]: operación inválida entre un valor 'numero' y uno 'texto'
```

### Operador unario con tipo incorrecto

El menos unario (`-`) requiere un `numero`; la negación lógica (`no`) requiere un
`booleano`.

```elevator
ascensor torre pisos 5;
var x : numero = -verdadero;
```

```text
Error semántico [línea 2, columna 18]: el operador unario requiere un valor 'numero', no 'booleano'
```

### Condición no booleana

La condición de un `si` y la de un `mientras` deben ser de tipo `booleano`.

```elevator
ascensor torre pisos 10;
si 5 { abrir; }
```

```text
Error semántico [línea 2, columna 4]: la condición debe ser de tipo 'booleano', no 'numero'
```

### Límites de `para` no numéricos

En `para i desde A hasta B`, los dos límites `A` y `B` deben ser de tipo
`numero`. La variable de control `i` es siempre `numero`.

```elevator
ascensor torre pisos 10;
para i desde verdadero hasta 3 { imprimir i; }
```

```text
Error semántico [línea 2, columna 14]: los límites de 'para' deben ser de tipo 'numero', no 'booleano'
```

!!! note "Impresión"
    `imprimir expr;` acepta una expresión de **cualquier** tipo (`numero`,
    `booleano` o `texto`): no impone restricciones semánticas sobre su argumento.

---

## Reglas del dominio del ascensor

Estas reglas son específicas de ElevatorLang: modelan el comportamiento físico de
un ascensor real. Para entenderlas en contexto, consulta también la guía
[El ascensor](../guia/ascensor.md).

### El ascensor debe estar declarado

Cualquier comando del ascensor (`subir`, `bajar`, `ir_a`, `abrir`, `cerrar`,
`esperar`) requiere que antes se haya declarado un ascensor.

```elevator
abrir;
```

```text
Error semántico [línea 1, columna 1]: no hay ningún ascensor declarado
```

### Un solo ascensor

Solo puede declararse **un** ascensor en todo el programa.

```elevator
ascensor a pisos 10;
ascensor b pisos 5;
```

```text
Error semántico [línea 2, columna 1]: el ascensor ya fue declarado
```

### El número de pisos debe ser un entero positivo

En `ascensor A pisos N;`, el valor `N` debe ser, por tipo, un `numero`; y, cuando
es una constante conocida, un **entero positivo**. Define el rango de pisos
`0..N`. El ascensor arranca en el piso `0` con la puerta cerrada.

Si el valor no es numérico:

```elevator
ascensor torre pisos verdadero;
```

```text
Error semántico [línea 1, columna 1]: el número de pisos debe ser de tipo 'numero', no 'booleano'
```

Si es numérico pero no un entero positivo (por ejemplo, `0`):

```elevator
ascensor torre pisos 0;
```

```text
Error semántico [línea 1, columna 1]: el número de pisos debe ser un entero positivo
```

### El argumento de un comando debe ser numérico

Los comandos con argumento (`subir`, `bajar`, `ir_a`, `esperar`) exigen que su
argumento sea de tipo `numero`.

```elevator
ascensor torre pisos 10;
subir "dos";
```

```text
Error semántico [línea 2, columna 1]: el argumento de 'subir' debe ser de tipo 'numero', no 'texto'
```

### Puerta cerrada para moverse

El ascensor no puede moverse con la puerta abierta: `subir`, `bajar` e `ir_a`
exigen que la puerta esté cerrada. Tras `abrir`, hay que `cerrar` antes de mover.

```elevator
ascensor torre pisos 10;
abrir;
subir 2;
```

```text
Error semántico [línea 3, columna 1]: no se puede mover el ascensor con la puerta abierta; falta 'cerrar'
```

### El movimiento debe ser positivo

La cantidad de pisos de `subir` y `bajar` debe ser **positiva** (mayor que cero).
Para *bajar*, no se escribe un número negativo: se usa el comando `bajar`.

```elevator
ascensor torre pisos 10;
subir 0;
```

```text
Error semántico [línea 2, columna 1]: el movimiento de 'subir' debe ser positivo
```

### La espera debe ser positiva

El tiempo de `esperar N segundos;` también debe ser positivo.

```elevator
ascensor torre pisos 10;
esperar 0 segundos;
```

```text
Error semántico [línea 2, columna 1]: el tiempo de espera debe ser positivo
```

### El movimiento no puede exceder el rango de pisos

El ascensor no puede salirse del rango `0..N`. El analizador comprueba dos casos,
con dos mensajes distintos:

Ir directamente a un piso fuera del rango (`ir_a`):

```elevator
ascensor torre pisos 5;
ir_a 8;
```

```text
Error semántico [línea 2, columna 1]: no se puede ir al piso 8: excede el rango (0..5)
```

Moverse (`subir` o `bajar`) una cantidad que rebasa el techo o el suelo:

```elevator
ascensor torre pisos 5;
ir_a 3;
subir 10;
```

```text
Error semántico [línea 3, columna 1]: desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)
```

---

## Seguimiento del estado del ascensor

Para comprobar el rango de pisos, el analizador simula de forma abstracta el
**estado del ascensor** a medida que recorre el programa: el piso actual, el
estado de la puerta y el rango de pisos. La política es:

> **Exacto en línea recta, desconocido tras ramas ambiguas.**

### En línea recta: el piso se sigue con exactitud

Mientras el código avanza de forma lineal y los argumentos son **constantes**, el
analizador conoce el piso exacto y puede comprobar cada movimiento contra el
rango sin margen de error. En `ir_a 3; subir 10;` sabe que parte del piso `3` y
detecta el desbordamiento.

### Argumentos con variables: piso desconocido

Si el argumento de un movimiento es una **variable** (o cualquier expresión no
constante), el analizador no puede saber a qué piso lleva, así que marca el piso
como **desconocido**. No inventa un valor ni reporta un falso positivo. El rango
se vuelve a comprobar en cuanto un `ir_a` con valor constante restablece un piso
conocido.

```elevator
ascensor torre pisos 5;
var n : numero = 3;
subir n;
ir_a 9;
```

```text
Error semántico [línea 4, columna 1]: no se puede ir al piso 9: excede el rango (0..5)
```

El `subir n` no se comprueba (el piso queda desconocido), pero `ir_a 9` sí, porque
es una constante fuera del rango.

### Tras ramas ambiguas: piso desconocido

Cuando un `si`, un `mientras` o un `para` deja el ascensor en pisos **distintos**
según el camino que se tome, el piso resultante no puede determinarse y pasa a
**desconocido**. Las comprobaciones de rango se **posponen** —sin falsos
positivos— hasta que un `ir_a` constante restablece un piso conocido.

En este programa, las dos ramas del `si` dejan al ascensor en pisos diferentes (3
y 1), de modo que después el piso es desconocido y `subir 100` **no** dispara
ningún error:

```elevator
ascensor torre pisos 5;
ir_a 2;
si verdadero {
    subir 1;
} sino {
    bajar 1;
}
subir 100;
```

```text
Análisis correcto: no se encontraron errores.
```

En cuanto un `ir_a` con valor constante fija de nuevo el piso, las comprobaciones
se reanudan:

```elevator
ascensor torre pisos 5;
ir_a 2;
si verdadero {
    subir 1;
} sino {
    bajar 1;
}
subir 100;
ir_a 9;
```

```text
Error semántico [línea 9, columna 1]: no se puede ir al piso 9: excede el rango (0..5)
```

!!! warning "Dentro de cada rama el estado sí se analiza"
    El cuerpo de cada rama se analiza a partir del estado conocido **a la
    entrada** de la rama. Por eso, un movimiento que se sale del rango *dentro*
    de un `si` o un bucle sí se detecta; lo que se vuelve desconocido es el piso
    **después** de la estructura, al unir los caminos posibles.

---

## Resumen de mensajes

| Regla | Mensaje exacto |
| --- | --- |
| Variable no declarada | `la variable 'x' no ha sido declarada` |
| Redeclaración en el ámbito | `la variable 'x' ya fue declarada en este ámbito` |
| Uso antes de asignar | `la variable 'x' se usa antes de asignarle un valor` |
| Asignación con tipo incompatible | `no se puede asignar un valor de tipo 'booleano' a la variable 'x' de tipo 'numero'` |
| Operandos incorrectos | `los operandos deben ser de tipo 'numero', pero son 'numero' y 'texto'` |
| Igualdad entre tipos distintos | `operación inválida entre un valor 'numero' y uno 'texto'` |
| Unario con tipo incorrecto | `el operador unario requiere un valor 'numero', no 'booleano'` |
| Condición no booleana | `la condición debe ser de tipo 'booleano', no 'numero'` |
| Límites de `para` no numéricos | `los límites de 'para' deben ser de tipo 'numero', no 'booleano'` |
| Argumento de comando no numérico | `el argumento de 'subir' debe ser de tipo 'numero', no 'texto'` |
| Sin ascensor declarado | `no hay ningún ascensor declarado` |
| Ascensor ya declarado | `el ascensor ya fue declarado` |
| Pisos no numéricos | `el número de pisos debe ser de tipo 'numero', no 'booleano'` |
| Pisos no enteros positivos | `el número de pisos debe ser un entero positivo` |
| Mover con la puerta abierta | `no se puede mover el ascensor con la puerta abierta; falta 'cerrar'` |
| Movimiento no positivo | `el movimiento de 'subir' debe ser positivo` |
| Espera no positiva | `el tiempo de espera debe ser positivo` |
| `ir_a` fuera de rango | `no se puede ir al piso 8: excede el rango (0..5)` |
| `subir` / `bajar` fuera de rango | `desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)` |

Para la lista completa de errores de las tres fases, consulta
[Errores](errores.md).
