# Gramática (EBNF)

Esta página reproduce la **gramática formal** de ElevatorLang en notación EBNF
(*Extended Backus–Naur Form*). Describe cómo se combinan los tokens del lenguaje
para formar programas correctos: declaraciones, comandos del ascensor,
expresiones y estructuras de control.

!!! note "Relación con las otras referencias"
    La gramática define la **forma** de los programas (fase sintáctica). Para los
    símbolos que la alimentan consulta la [referencia de tokens](tokens.md); para
    las restricciones de significado, las [reglas semánticas](semantica.md).

## Notación

La gramática usa un conjunto reducido de metasímbolos EBNF:

| Símbolo | Significado |
| ------- | ----------- |
| `=`     | **definición**: asocia un nombre con su regla. |
| `\|`     | **alternativa**: una opción u otra. |
| `{ }`   | **repetición**: cero o más veces. |
| `[ ]`   | **opcional**: cero o una vez. |
| `( )`   | **agrupación**: agrupa varios elementos. |
| `" "`   | **terminal literal**: texto que aparece tal cual en el programa. |
| `? ?`   | **descripción informal** de un terminal (en lenguaje natural). |

!!! tip "Siete niveles de precedencia"
    Las reglas de expresión (`expr_o`, `expr_y`, `expr_igualdad`,
    `expr_relacional`, `expr_aditiva`, `expr_mult`, `expr_unaria`) codifican
    directamente en la gramática los **7 niveles de precedencia** de operadores,
    de menor a mayor. Cuanto más abajo aparece la regla, más fuerte liga el
    operador. Los detalles de cada nivel están en
    [Expresiones y operadores](../guia/expresiones.md).

## Gramática completa

```
(* ================================================================= *)
(* Gramatica formal de ElevatorLang  -  notacion EBNF                 *)
(* DSL para programar el comportamiento de un ascensor.               *)
(*                                                                     *)
(* Convenciones:                                                       *)
(*   =      definicion          |    alternativa                       *)
(*   { }    cero o mas          [ ]  opcional                          *)
(*   ( )    agrupacion          " "  terminal literal                  *)
(*   ? ?    descripcion informal de un terminal                        *)
(* ================================================================= *)

programa             = { sentencia } ;

sentencia            = declaracion_ascensor
                     | declaracion_variable
                     | asignacion
                     | comando_ascensor
                     | sentencia_si
                     | sentencia_mientras
                     | sentencia_para
                     | sentencia_imprimir
                     | bloque ;

(* --- Declaraciones --- *)
declaracion_ascensor = "ascensor" , identificador , "pisos" , expresion , ";" ;
declaracion_variable = "var" , identificador , ":" , tipo , [ "=" , expresion ] , ";" ;
tipo                 = "numero" | "booleano" | "texto" ;

(* --- Asignacion --- *)
asignacion           = identificador , "=" , expresion , ";" ;

(* --- Comandos de dominio (ascensor) --- *)
comando_ascensor     = comando_movimiento
                     | comando_puerta
                     | comando_esperar ;
comando_movimiento   = ( "subir" | "bajar" | "ir_a" ) , expresion , ";" ;
comando_puerta       = ( "abrir" | "cerrar" ) , ";" ;
comando_esperar      = "esperar" , expresion , "segundos" , ";" ;

(* --- Estructuras de control --- *)
sentencia_si         = "si" , expresion , bloque , [ "sino" , bloque ] ;
sentencia_mientras   = "mientras" , expresion , bloque ;
sentencia_para       = "para" , identificador , "desde" , expresion ,
                       "hasta" , expresion , bloque ;
sentencia_imprimir   = "imprimir" , expresion , ";" ;
bloque               = "{" , { sentencia } , "}" ;

(* --- Expresiones (de menor a mayor precedencia) --- *)
expresion            = expr_o ;
expr_o               = expr_y           , { "o"  , expr_y } ;
expr_y               = expr_igualdad    , { "y"  , expr_igualdad } ;
expr_igualdad        = expr_relacional  , { ( "==" | "!=" ) , expr_relacional } ;
expr_relacional      = expr_aditiva     , { ( "<" | ">" | "<=" | ">=" ) , expr_aditiva } ;
expr_aditiva         = expr_mult        , { ( "+" | "-" ) , expr_mult } ;
expr_mult            = expr_unaria      , { ( "*" | "/" ) , expr_unaria } ;
expr_unaria          = ( "no" | "-" ) , expr_unaria
                     | primario ;
primario             = literal_numero
                     | literal_texto
                     | literal_booleano
                     | identificador
                     | "(" , expresion , ")" ;

(* --- Terminales lexicos --- *)
identificador        = ( letra | "_" ) , { letra | digito | "_" } ;
literal_numero       = digito , { digito } , [ "." , digito , { digito } ] ;
literal_texto        = '"' , { caracter_texto | secuencia_escape } , '"' ;
literal_booleano     = "verdadero" | "falso" ;
secuencia_escape     = barra , ( "n" | "t" | '"' | barra ) ;
barra                = ? una barra invertida (backslash) ? ;

letra                = "a" … "z" | "A" … "Z" ;
digito               = "0" … "9" ;
caracter_texto       = ? cualquier caracter excepto comilla doble, barra
                         invertida o salto de linea ? ;

(* --- Comentarios (descartados por el analizador lexico) --- *)
comentario_linea     = "//" , { ? cualquier caracter excepto salto de linea ? } ;
comentario_bloque    = "/*" , { ? cualquier caracter ? } , "*/" ;
(* El comentario de bloque termina en el primer "*/" y no anida. *)

(* ================================================================= *)
(* Notas:                                                              *)
(*  - Los numeros con signo se obtienen mediante 'expr_unaria' ("-").  *)
(*  - La gramatica define 7 niveles de precedencia (o, y, igualdad,    *)
(*    relacional, aditiva, multiplicativa, unaria); el minimo exigido  *)
(*    por las orientaciones generales es 3.                            *)
(* ================================================================= *)
```

## Notas sobre la gramática

!!! warning "No hay literales numéricos negativos"
    Observa que `literal_numero` solo produce dígitos (y un punto decimal
    opcional): **nunca** incluye un signo. Los números con signo se obtienen
    aplicando el **operador unario `-`** de la regla `expr_unaria`. Es decir,
    `-3` se analiza como la negación unaria del literal `3`, no como un único
    literal `-3`.

    ```
    var x : numero = -3;
    ```

Algunas observaciones que ayudan a leer la gramática:

- **Un programa es una secuencia de sentencias** (`programa = { sentencia }`),
  posiblemente vacía. La declaración del ascensor es una sentencia más, no un
  encabezado obligatorio impuesto por la sintaxis; quién y cuántas veces puede
  declararlo lo deciden las [reglas semánticas](semantica.md).
- **El inicializador de una variable es opcional**: la parte `[ "=" , expresion ]`
  de `declaracion_variable` permite tanto `var x : numero = 5;` como
  `var x : numero;`.
- **El `sino` es opcional**: en `sentencia_si`, la rama `[ "sino" , bloque ]`
  puede omitirse.
- **Los bloques introducen ámbitos**: `bloque = "{" , { sentencia } , "}"`, y un
  bloque es a su vez una sentencia, por lo que puede anidarse.
- **Los comentarios no aparecen en las reglas de sentencia**: el analizador
  léxico los descarta antes de la fase sintáctica, de modo que pueden situarse
  entre cualesquiera tokens sin afectar a la estructura del programa.

!!! example "De la gramática al programa"
    Este fragmento ejercita varias reglas a la vez —declaración del ascensor,
    variable con inicializador, comandos de movimiento y puerta, espera y un
    condicional con `sino`— y es un programa válido:

    ```
    ascensor torre pisos 10;

    var destino : numero = 5;

    ir_a destino;
    abrir;
    esperar 3 segundos;
    cerrar;

    si destino > 3 {
        subir 2;
    } sino {
        bajar 1;
    }
    ```

## Véase también

- [Tokens](tokens.md) — los símbolos terminales que consume esta gramática.
- [Reglas semánticas](semantica.md) — restricciones de significado que la
  sintaxis por sí sola no captura.
- [Expresiones y operadores](../guia/expresiones.md) — los 7 niveles de
  precedencia explicados con ejemplos.
- [Formato de errores](errores.md) — cómo se reportan los fallos sintácticos.
