# Comandos del ascensor

Esta página describe el corazón del dominio de ElevatorLang: la **declaración del
ascensor** y los **comandos** que controlan su movimiento, sus puertas y sus
esperas. También explica las tres reglas semánticas del dominio y la política con
la que el analizador sigue la pista del piso actual.

!!! note "Un solo ascensor por programa"
    Un programa de ElevatorLang controla **un único** ascensor. Debe declararse
    antes de usar cualquier comando; de lo contrario, cada comando produce el
    error `no hay ningún ascensor declarado`.

## Declarar el ascensor

La declaración fija el rango de pisos y el estado inicial del ascensor:

```elevator
ascensor torre pisos 10;
```

Esta línea declara un ascensor llamado `torre` con **11 pisos válidos**,
numerados del **0** al **10** (el rango es `0..N`). Al declararse, el ascensor
parte de un estado conocido:

- **Piso inicial:** `0`.
- **Puerta:** cerrada.

!!! warning "Reglas de la declaración"
    - Solo puede haber un ascensor. Una segunda declaración produce
      `el ascensor ya fue declarado`.
    - El número de pisos debe ser **un entero positivo**. Si es una constante que
      no cumple (por ejemplo `0`, un negativo o un decimal no entero), el error es
      `el número de pisos debe ser un entero positivo`.
    - El número de pisos debe ser de tipo `numero`. Si no, el error es
      `el número de pisos debe ser de tipo 'numero', no '<tipo>'`.

Si el número de pisos no es una constante (por ejemplo, una variable), el
analizador **no puede conocer el rango**: la declaración se acepta, pero las
comprobaciones de rango quedan desactivadas para ese programa.

## Comandos de movimiento

Hay dos formas de mover el ascensor: por destino **absoluto** y por
desplazamiento **relativo**.

| Comando | Tipo | Significado |
|---------|------|-------------|
| `ir_a N;` | absoluto | va directamente al piso `N` |
| `subir N;` | relativo | sube `N` pisos desde el piso actual |
| `bajar N;` | relativo | baja `N` pisos desde el piso actual |

```elevator
ascensor torre pisos 10;

ir_a 5;     // va al piso 5
subir 2;    // ahora está en el 7
bajar 1;    // ahora está en el 6
ir_a 0;     // vuelve al 0
```

!!! example "Programa válido completo"
    Un recorrido lineal que no viola ninguna regla del dominio:

    ```elevator
    ascensor torre pisos 10;

    ir_a 5;
    abrir;
    esperar 3 segundos;
    cerrar;

    subir 2;
    bajar 1;
    ir_a 0;
    abrir;
    ```

El argumento de cualquier comando de movimiento debe ser de tipo `numero`; si no,
el error es `el argumento de 'subir' debe ser de tipo 'numero', no '<tipo>'` (con
el comando correspondiente).

## Comandos de puerta

```elevator
abrir;
cerrar;
```

`abrir` deja la puerta **abierta** y `cerrar` la deja **cerrada**. No llevan
argumento. Su interacción con el movimiento se describe en la
[regla 2](#regla-2-puerta-cerrada-para-moverse).

## Esperar

```elevator
esperar 3 segundos;
```

Hace que el ascensor espere el número de segundos indicado. La palabra `segundos`
es obligatoria. El tiempo de espera debe ser **positivo** (ver
[regla 3](#regla-3-movimiento-y-espera-positivos)).

## Las tres reglas del dominio

El analizador simula de forma abstracta el estado del ascensor (piso y puerta)
para detectar tres errores propios del dominio. Todos los mensajes que se
muestran a continuación son **exactos**.

### Regla 1: el rango de pisos

!!! warning "Nunca salgas del rango `0..N`"
    Ningún movimiento puede llevar el ascensor por debajo del piso `0` ni por
    encima del piso máximo `N`.

Para `ir_a`, se comprueba el **destino**:

```elevator
ascensor torre pisos 5;
ir_a 8;
```

```text
Error semántico [línea 2, columna 1]: no se puede ir al piso 8: excede el rango (0..5)
```

Para `subir` y `bajar`, se comprueba el **piso resultante** a partir del piso
actual:

```elevator
ascensor torre pisos 5;
ir_a 3;
subir 10;
```

```text
Error semántico [línea 3, columna 1]: desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)
```

!!! tip
    El error de rango solo se emite cuando el analizador conoce el piso actual y
    el argumento es una constante. Si alguno es desconocido, la comprobación se
    pospone en lugar de generar un falso positivo (ver la
    [política de seguimiento del piso](#politica-de-seguimiento-del-piso)).

### Regla 2: puerta cerrada para moverse

!!! warning "Cierra antes de moverte"
    El ascensor no puede moverse con la puerta abierta. Hay que `cerrar` antes de
    `ir_a`, `subir` o `bajar`.

```elevator
ascensor torre pisos 5;
abrir;
subir 1;
```

```text
Error semántico [línea 3, columna 1]: no se puede mover el ascensor con la puerta abierta; falta 'cerrar'
```

La forma correcta es cerrar la puerta antes de volver a moverse:

```elevator
ascensor torre pisos 5;
ir_a 2;
abrir;
esperar 2 segundos;
cerrar;
subir 1;
```

### Regla 3: movimiento y espera positivos

!!! warning "Las cantidades deben ser positivas"
    `subir` y `bajar` exigen una cantidad **positiva**, y `esperar` un tiempo
    **positivo**. Para ir hacia abajo se usa `bajar`, no `subir` con un número
    negativo.

```elevator
ascensor torre pisos 5;
subir -1;
```

```text
Error semántico [línea 2, columna 1]: el movimiento de 'subir' debe ser positivo
```

```elevator
ascensor torre pisos 5;
esperar 0 segundos;
```

```text
Error semántico [línea 2, columna 1]: el tiempo de espera debe ser positivo
```

## Política de seguimiento del piso

El analizador sigue el piso del ascensor con la regla **«exacto en línea recta,
desconocido tras ramas ambiguas»**:

- **En línea recta:** mientras el código es lineal y los argumentos son
  constantes, el piso se conoce con exactitud y las comprobaciones de rango se
  aplican de inmediato.
- **Tras ramas ambiguas:** después de un `si`, un `mientras` o un `para` cuyo
  efecto sobre el piso no puede determinarse (por ejemplo, ramas que terminan en
  pisos distintos), el piso pasa a ser **DESCONOCIDO**. Con un piso desconocido,
  las comprobaciones de rango de `subir`/`bajar` se **posponen**: no se generan
  falsos positivos.
- **Restablecimiento:** un `ir_a <constante>` fija un destino conocido y vuelve a
  poner el piso en un valor exacto, reanudando las comprobaciones de rango.
- **Argumentos con variables:** si el argumento de un movimiento no es una
  constante (por ejemplo, una variable), el piso también queda **DESCONOCIDO**.

!!! example "El piso se vuelve desconocido y luego se restablece"
    ```elevator
    ascensor torre pisos 5;
    ir_a 2;

    si verdadero {
        subir 1;        // esta rama terminaría en el piso 3
    } sino {
        bajar 2;        // esta otra, en el piso 0
    }

    // Tras el 'si', el piso es DESCONOCIDO: las dos ramas difieren.
    subir 100;          // no se comprueba el rango: sin error

    ir_a 1;             // 'ir_a' restablece un piso conocido (1)
    subir 100;          // ahora SÍ se comprueba: error de rango desde el piso 1
    ```

    El primer `subir 100` no produce error porque el piso es desconocido; el
    segundo sí, porque `ir_a 1` restableció el piso a un valor exacto:

    ```text
    Error semántico [línea 14, columna 1]: desde el piso 1 no se puede subir 100 pisos: excede el rango (0..5)
    ```

!!! note "La puerta sigue la misma lógica"
    Igual que el piso, el estado de la puerta puede volverse desconocido cuando
    dos ramas la dejan en estados distintos. La comprobación de la
    [regla 2](#regla-2-puerta-cerrada-para-moverse) solo se dispara cuando el
    analizador sabe con certeza que la puerta está abierta.

## Véase también

- [Reglas semánticas](../referencia/semantica.md) — referencia completa de todas
  las comprobaciones del analizador.
- [Ejemplos](../ejemplos.md) — programas completos comentados.
