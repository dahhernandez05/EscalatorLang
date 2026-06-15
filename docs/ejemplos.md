# Ejemplos

Esta página recorre los **tres programas de prueba** incluidos en la carpeta
`examples/` del repositorio, uno por cada resultado posible del analizador:
un programa correcto, un error sintáctico y un error semántico. De cada uno se
muestra el código fuente íntegro, qué demuestra, el comando para ejecutarlo y la
**salida exacta** del analizador. Al final encontrarás dos ejemplos adicionales
para reforzar lo aprendido.

!!! note "Cómo ejecutar los ejemplos"
    Todos los programas usan la extensión `.asc` y se analizan con la
    [interfaz de línea de comandos](primeros-pasos/uso.md). El análisis se
    detiene en la **primera fase** que falla.

---

## 1. Programa válido

El archivo `examples/prueba_valida.asc` es correcto en las tres fases (léxica,
sintáctica y semántica). Demuestra el uso conjunto de variables, expresiones
aritméticas, control de flujo y comandos del ascensor **sin violar ninguna
regla del dominio**.

```elevator
// prueba_valida.asc
// Programa correcto en las tres fases: léxico, sintáctico y semántico.
// Usa variables, expresiones, control de flujo y comandos del ascensor
// sin violar ninguna regla del dominio.

ascensor torre pisos 10;

var piso_objetivo : numero = 5;
var mensaje : texto = "Subiendo al piso objetivo";

// Asignación con una expresión aritmética.
piso_objetivo = piso_objetivo + 1;

imprimir mensaje;

ir_a 5;
abrir;
esperar 3 segundos;
cerrar;

si piso_objetivo > 3 {
    subir 2;
} sino {
    bajar 1;
}

ir_a 0;
abrir;

/* Bucle contado que imprime un contador sin mover el ascensor. */
para i desde 1 hasta 3 {
    imprimir i;
}
```

**Qué demuestra:**

- Declaración del ascensor con su rango de pisos (`0..10`).
- Variables de tipo `numero` y `texto`, con inicializador.
- Asignación con una expresión aritmética (`piso_objetivo + 1`).
- Comandos del ascensor en línea recta: `ir_a`, `abrir`, `esperar`, `cerrar`.
- Un condicional `si … sino` y un bucle contado `para … desde … hasta`.

!!! tip "Seguimiento del piso"
    El analizador sigue el piso con exactitud mientras el código es lineal y los
    argumentos son constantes. Tras el `si` el piso pasa a ser **desconocido**,
    pero el `ir_a 0;` posterior restablece un piso conocido, así que no hay
    falsos positivos de rango. Lee más en
    [reglas semánticas](referencia/semantica.md).

Ejecútalo con:

```bash
uv run python -m elevator_lang examples/prueba_valida.asc
```

Salida:

```text
Análisis correcto: no se encontraron errores.
```

El código de salida es `0`.

---

## 2. Error sintáctico

El archivo `examples/prueba_error_sintactico.asc` tiene un único fallo: falta el
`;` al final de la declaración del ascensor. El parser espera un `;` y, en su
lugar, encuentra el siguiente comando, `ir_a`.

```elevator
// prueba_error_sintactico.asc
// Programa con un error sintáctico: falta el ';' al final de la
// declaración del ascensor, por lo que el parser espera ';' y encuentra 'ir_a'.

ascensor torre pisos 10
ir_a 5;
abrir;
```

**Qué demuestra:** cómo el analizador localiza un error de estructura y reporta
**qué** esperaba y **qué** encontró, con la posición exacta. La posición
señalada (línea 6, columna 1) corresponde al primer token inesperado, `ir_a`,
ya que es ahí donde se hace evidente que faltaba el `;`.

Ejecútalo con:

```bash
uv run python -m elevator_lang examples/prueba_error_sintactico.asc
```

Salida:

```text
Error sintáctico [línea 6, columna 1]: se esperaba ';', se encontró 'ir_a'

Se encontró 1 error.
```

El código de salida es `1`.

---

## 3. Error semántico

El archivo `examples/prueba_error_semantico.asc` es léxica y sintácticamente
correcto, pero **viola una regla del dominio**: el ascensor solo tiene 5 pisos
y, estando en el piso 3, intenta `subir 10`, lo que excede el rango `0..5`.

```elevator
// prueba_error_semantico.asc
// Programa sintácticamente correcto, pero semánticamente inválido:
// 'subir 10' desde el piso 3 excede el rango (0..5) del ascensor.

ascensor torre pisos 5;
imprimir "Iniciando secuencia";
ir_a 3;
subir 10;
```

**Qué demuestra:** el control de **rango de pisos**. El analizador sigue el piso
en línea recta (`ir_a 3;` deja el ascensor en el piso 3) y detecta que subir 10
pisos lo llevaría más allá del piso máximo.

Ejecútalo con:

```bash
uv run python -m elevator_lang examples/prueba_error_semantico.asc
```

Salida:

```text
Error semántico [línea 8, columna 1]: desde el piso 3 no se puede subir 10 pisos: excede el rango (0..5)

Se encontró 1 error.
```

El código de salida es `1`.

---

## Ejemplos adicionales

### Válido: variables y control de flujo

Este programa combina variables, un condicional `si … sino`, un bucle
`mientras` y movimiento del ascensor con la puerta correctamente cerrada antes
de moverse.

```elevator
// Ejemplo adicional válido: variables, condicional y bucle 'mientras'.
ascensor edificio pisos 8;

var destino : numero = 6;
var visitas : numero = 0;

// Si el destino es alto, avisamos antes de subir.
si destino >= 5 {
    imprimir "Subiendo a un piso alto";
} sino {
    imprimir "Piso bajo";
}

ir_a destino;
abrir;
esperar 2 segundos;
cerrar;

// Contamos algunas visitas con un bucle 'mientras'.
mientras visitas < 3 {
    imprimir visitas;
    visitas = visitas + 1;
}
```

Salida:

```text
Análisis correcto: no se encontraron errores.
```

!!! example "Argumentos con variables"
    Aquí `ir_a destino;` usa una variable en lugar de una constante. El
    analizador no puede seguir el piso resultante, así que pasa a ser
    **desconocido** y pospone las comprobaciones de rango, evitando falsos
    positivos. Esto es válido y forma parte de la política de seguimiento del
    piso.

### Error de dominio: mover con la puerta abierta

Una de las reglas del dominio prohíbe mover el ascensor mientras la puerta está
abierta. Aquí se abre la puerta y, sin volver a cerrarla, se intenta `subir`.

```elevator
// Ejemplo adicional con error de dominio: mover con la puerta abierta.
ascensor torre pisos 10;

ir_a 2;
abrir;
subir 3;   // falta 'cerrar' antes de moverse
```

Salida:

```text
Error semántico [línea 6, columna 1]: no se puede mover el ascensor con la puerta abierta; falta 'cerrar'

Se encontró 1 error.
```

El código de salida es `1`. Para corregirlo, añade `cerrar;` antes de `subir 3;`.

!!! warning "Una fase a la vez"
    Recuerda que el análisis se detiene en la primera fase con errores. Si un
    programa tiene a la vez un error sintáctico y uno semántico, solo verás el
    sintáctico hasta que lo corrijas. Consulta el
    [formato de los errores](referencia/errores.md) para más detalles.
