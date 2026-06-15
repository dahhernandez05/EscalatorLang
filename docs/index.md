# ElevatorLang

**ElevatorLang** es un lenguaje de dominio específico (DSL) para programar el
comportamiento de un ascensor: subir, bajar, abrir y cerrar puertas, esperar e
ir a un piso. Junto al lenguaje viene su **analizador**, que lee un programa,
lo valida en tres fases y reporta los errores con su posición exacta.

!!! note "Qué hace (y qué no)"
    El analizador **lee, valida y reporta** errores significativos. **No genera
    código máquina**: su único objetivo es comprobar que el programa es correcto
    en las fases léxica, sintáctica y semántica.

## Un vistazo rápido

Un programa de ElevatorLang se guarda con extensión `.asc`. Este ejemplo declara
un ascensor, usa una variable, mueve la cabina y ramifica con un condicional:

```
ascensor torre pisos 10;

var destino : numero = 5;
imprimir "Subiendo al piso objetivo";

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

Para analizarlo:

```bash
uv run python -m elevator_lang programa.asc
```

```text
Análisis correcto: no se encontraron errores.
```

## Características

- **Tres fases de análisis.** Léxico, sintáctico y semántico, en ese orden. El
  análisis se detiene en la **primera fase** que encuentra errores, porque cada
  fase necesita la salida correcta de la anterior.
- **Tres reglas del dominio del ascensor.** Movimientos dentro del rango de
  pisos `0..N`, puerta cerrada antes de moverse y cantidades de movimiento
  positivas. Más detalles en [El ascensor](guia/ascensor.md).
- **Variables, expresiones y control de flujo.** Tipos `numero`, `booleano` y
  `texto`; operadores aritméticos, relacionales y lógicos con siete niveles de
  precedencia; condicionales `si`/`sino`, bucles `mientras` y bucles contados
  `para`.
- **Errores posicionados en español.** Todos los diagnósticos indican línea y
  columna y describen la causa en español:

  ```text
  Error léxico     [línea L, columna C]: <descripción>
  Error sintáctico [línea L, columna C]: se esperaba X, se encontró Y
  Error semántico  [línea L, columna C]: <regla violada>
  ```

!!! tip "Seguimiento del piso"
    El analizador sigue el piso actual con exactitud mientras el código avanza
    en línea recta. Tras una rama ambigua (`si`, `mientras`, `para`) el piso
    pasa a ser desconocido y las comprobaciones de rango se posponen, sin
    falsos positivos, hasta que un `ir_a` con valor constante restablece la
    posición.

## Por dónde seguir

- [Primeros pasos: instalación](primeros-pasos/instalacion.md) — instala el
  proyecto y deja el entorno listo.
- [Primeros pasos: uso](primeros-pasos/uso.md) — analiza tu primer programa y
  entiende los códigos de salida.
- [Ejemplos](ejemplos.md) — programas válidos y con errores, comentados paso a
  paso.
