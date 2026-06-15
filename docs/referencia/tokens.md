# Tabla de tokens

Un **token** es la unidad léxica mínima que el analizador reconoce en el código
fuente: una palabra reservada, un identificador, un literal, un operador o un
delimitador. El [analizador léxico](../primeros-pasos/uso.md) recorre el texto de
un programa `.asc`, descarta los espacios en blanco y los comentarios, y produce
la secuencia de tokens que después consumen las fases sintáctica y semántica.

Esta página es el catálogo completo de las clases de token de ElevatorLang. Cada
clase se describe con su **patrón** (en estilo expresión regular) y un ejemplo. La
tabla coincide exactamente con los tipos de token reales (`TokenType`) definidos
en el código.

!!! note "El espacio en blanco y los comentarios no son tokens"
    Los espacios, tabuladores y saltos de línea solo separan tokens; nunca
    producen uno. Los [comentarios](#comentarios) se descartan por completo
    durante el escaneo. El único token que no proviene del texto fuente es `EOF`,
    que el lexer añade al final para marcar el fin de la entrada.

## Palabras reservadas

Las palabras reservadas son identificadores con un significado fijo en el
lenguaje; **no pueden usarse como nombres de variable**. Todas coinciden con el
patrón de un identificador, pero el lexer las reconoce primero y les asigna su
tipo propio.

Se dividen en dos grupos: las del **dominio** (el ascensor y sus comandos) y las
del **núcleo** (declaraciones, tipos, control de flujo y operadores con nombre).

| Grupo   | Palabras reservadas |
| ------- | ------------------- |
| Dominio | `ascensor` · `pisos` · `subir` · `bajar` · `ir_a` · `abrir` · `cerrar` · `esperar` · `segundos` |
| Núcleo  | `var` · `numero` · `booleano` · `texto` · `si` · `sino` · `mientras` · `para` · `desde` · `hasta` · `imprimir` · `verdadero` · `falso` · `y` · `o` · `no` |

!!! warning "Distinción entre mayúsculas y minúsculas"
    Las palabras reservadas se escriben en minúsculas. `Var` o `SUBIR` no son
    palabras reservadas: se interpretarían como identificadores comunes.

## Identificadores

Un identificador nombra una variable o el ascensor. Comienza por una letra ASCII
o un guion bajo, y continúa con letras, dígitos o guiones bajos.

| Clase de token | Patrón | Ejemplos |
| -------------- | ------ | -------- |
| `IDENTIFICADOR` | `[a-zA-Z_][a-zA-Z0-9_]*` | `piso`, `piso_objetivo`, `_temp`, `contador2`, `torre` |

!!! note "Solo ASCII"
    El lexer reconoce únicamente letras ASCII (`a`–`z`, `A`–`Z`) y el guion bajo
    como carácter inicial. Las tildes y la `ñ` **no** forman parte de un
    identificador válido.

## Literales

### Literal numérico

Un número es una secuencia de dígitos, opcionalmente con una parte decimal. Si
aparece un punto, debe ir seguido de al menos un dígito; un literal numérico
nunca termina en punto. Los números **negativos** se obtienen aplicando el
operador unario `-` a un literal positivo, no como parte del propio token.

| Clase de token | Patrón | Ejemplos |
| -------------- | ------ | -------- |
| `NUMERO_LITERAL` (entero)  | `[0-9]+` | `0`, `5`, `42`, `10` |
| `NUMERO_LITERAL` (decimal) | `[0-9]+\.[0-9]+` | `3.5`, `0.0`, `100.25` |

Un literal sin punto se escanea como entero; uno con punto, como decimal. Ambos
casos producen el mismo tipo de token (`NUMERO_LITERAL`) y, semánticamente, el
mismo tipo del lenguaje: [`numero`](../guia/tipos.md).

### Literal de texto

Una cadena va encerrada entre comillas dobles y puede contener secuencias de
escape. No puede abarcar varias líneas: un salto de línea antes de la comilla de
cierre es un [error léxico](errores.md).

| Clase de token | Patrón | Ejemplos |
| -------------- | ------ | -------- |
| `TEXTO_LITERAL` | `"([^"\\\n]\|\\[nt"\\])*"` | `"hola"`, `"Piso 1"`, `"linea\n"`, `"comilla \" interna"` |

Las secuencias de escape reconocidas dentro de una cadena son:

| Escape | Significado            |
| ------ | ---------------------- |
| `\n`   | salto de línea         |
| `\t`   | tabulador              |
| `\"`   | comilla doble literal  |
| `\\`   | barra invertida literal|

!!! warning "Escapes no reconocidos"
    Cualquier otra secuencia tras la barra invertida (por ejemplo `\x`) es un
    error léxico. Consulta los mensajes en la
    [referencia de errores](errores.md).

### Literales booleanos

Los dos valores de tipo [`booleano`](../guia/tipos.md) son palabras reservadas
con su propio tipo de token; no son identificadores.

| Clase de token | Patrón        | Ejemplo      |
| -------------- | ------------- | ------------ |
| `VERDADERO`    | `verdadero`   | `verdadero`  |
| `FALSO`        | `falso`       | `falso`      |

## Operadores

Los operadores combinan o transforman valores dentro de una expresión. Su
significado y precedencia se detallan en
[Expresiones y operadores](../guia/expresiones.md); aquí solo figuran como
tokens.

| Clase de token | Patrón | Significado         |
| -------------- | ------ | ------------------- |
| `MAS`          | `+`    | suma                |
| `MENOS`        | `-`    | resta / negación unaria |
| `POR`          | `*`    | multiplicación      |
| `ENTRE`        | `/`    | división            |
| `ASIGNAR`      | `=`    | asignación          |
| `IGUAL`        | `==`   | igual a             |
| `DISTINTO`     | `!=`   | distinto de         |
| `MENOR`        | `<`    | menor que           |
| `MAYOR`        | `>`    | mayor que           |
| `MENOR_IGUAL`  | `<=`   | menor o igual que   |
| `MAYOR_IGUAL`  | `>=`   | mayor o igual que   |

!!! note "Operadores con nombre"
    La conjunción (`y`), la disyunción (`o`) y la negación lógica (`no`) **no**
    son símbolos: son [palabras reservadas](#palabras-reservadas) y se escanean
    como tales.

!!! warning "El carácter `!` aislado no es un token"
    `!` solo es válido como parte de `!=`. Un `!` suelto produce un error léxico:
    no existe el operador de negación con símbolo.

## Delimitadores

Los delimitadores estructuran el código: agrupan expresiones, delimitan bloques y
terminan sentencias o introducen el tipo de una variable.

| Clase de token | Patrón | Uso                                   |
| -------------- | ------ | ------------------------------------- |
| `PAREN_IZQ`    | `(`    | abre una agrupación de expresión      |
| `PAREN_DER`    | `)`    | cierra una agrupación de expresión    |
| `LLAVE_IZQ`    | `{`    | abre un bloque                        |
| `LLAVE_DER`    | `}`    | cierra un bloque                      |
| `PUNTO_COMA`   | `;`    | termina una sentencia                 |
| `DOS_PUNTOS`   | `:`    | separa el nombre de su tipo en `var`  |

!!! note "No existe la coma"
    ElevatorLang no usa la coma `,` en ninguna construcción. Encontrar una `,` en
    el código produce un error léxico.

## Comentarios

Los comentarios documentan el código y el analizador los **descarta** por
completo: no generan ningún token. Hay dos formas.

| Forma          | Patrón          | Descripción                                    |
| -------------- | --------------- | ---------------------------------------------- |
| De línea       | `// ...`        | desde `//` hasta el final de la línea          |
| De bloque      | `/* ... */`     | desde `/*` hasta el primer `*/`; no anida      |

```
// Esto es un comentario de línea.
ir_a 5;   // También puede ir al final de una sentencia.

/* Esto es un comentario
   de bloque que abarca varias líneas. */
abrir;
```

!!! warning "Comentario de bloque sin cerrar"
    Un `/*` sin su `*/` correspondiente llega hasta el final del archivo y produce
    un error léxico. Además, el bloque **no anida**: termina en el primer `*/` que
    encuentra.

## Fin de la entrada

| Clase de token | Patrón | Descripción                                  |
| -------------- | ------ | -------------------------------------------- |
| `EOF`          | —      | marcador que el lexer añade al final del texto |

`EOF` no proviene de ningún carácter del código: el analizador lo emite siempre
como último token para señalar que no queda más entrada por leer.

## Ejemplo de tokenización

El siguiente programa usa, en conjunto, casi todas las clases de token de la
tabla:

```
ascensor torre pisos 10;

// Identificadores, literales y operadores
var contador : numero = 0;
var altura : numero = 3.5;
var mensaje : texto = "Piso \"1\"\n";
var activo : booleano = verdadero;

contador = (contador + 1) * 2;
activo = no (contador >= 10) y altura < 100.0;

si activo == falso o contador != 0 {
    imprimir mensaje;
}

/* Comentario
   de bloque */
ir_a 5;
abrir;
esperar 2 segundos;
cerrar;
```

Al analizarlo, no se encuentra ningún error:

```text
Análisis correcto: no se encontraron errores.
```

---

Para ver cómo se combinan estos tokens en construcciones completas, consulta la
[gramática](gramatica.md). El formato exacto de los diagnósticos léxicos está en
la [referencia de errores](errores.md), y los tipos del lenguaje a los que dan
lugar los literales, en [Tipos](../guia/tipos.md).
