# Owner(s): Sergio Carrillo 14-11315 y David Pereira 18-10245
# Date: 15 de junio de 2025 (Actualizado)
# Description: Proyecto Etapa2 CI-3725 Traductores e Interpretadores -
#              Implementación de un analizador sintáctico para un lenguaje imperativo,
#              con construcción de un Árbol de Sintaxis Abstracta (AST),
#              utilizando el analizador léxico de lexer.py.

import ply.yacc as Yacc  # Importa el módulo Yacc de PLY para el analizador sintáctico
import sys               # Importa el módulo sys para acceder a argumentos de línea de comandos y salir del programa
from lexer import get_lexer_and_tokens, tokens # Importa la función para obtener el lexer y la lista de tokens

def main():
    """
    Función principal del programa.
    Gestiona la entrada de archivos, el proceso de análisis léxico y sintáctico,
    y la impresión del Árbol de Sintaxis Abstracta (AST) resultante.
    """
    # --------------------------------------------------------------------------
    # Gestión de la entrada de archivos
    # --------------------------------------------------------------------------
    # Verifica que se haya proporcionado exactamente un argumento de línea de comandos (el nombre del archivo).
    if len(sys.argv) != 2:
        print("Error: Por favor proporcione un archivo .imperat como argumento")
        print("Uso: python parse.py archivo.imperat")
        sys.exit(1) # Sale del programa con un código de error

    # Verifica que el archivo proporcionado tenga la extensión '.imperat'.
    if not sys.argv[1].endswith('.imperat'):
        print("Error: El archivo debe tener extensión .imperat")
        sys.exit(1) # Sale del programa con un código de error

    # Intenta abrir y leer el contenido del archivo de entrada.
    try:
        with open(sys.argv[1], 'r') as file:
            input_data = file.read()
    except FileNotFoundError:
        # Captura el error si el archivo no se encuentra
        print(f"Error: No se encontró el archivo {sys.argv[1]}")
        sys.exit(1)
    except Exception as e:
        # Captura cualquier otro error durante la lectura del archivo
        print(f"Error al leer el archivo: {str(e)}")
        sys.exit(1)

    # --------------------------------------------------------------------------
    # Inicialización del Analizador Léxico (Lexer)
    # --------------------------------------------------------------------------
    # Obtiene el lexer configurado y la lista de errores léxicos desde el módulo lexer.py.
    lexer, lexer_tokens, lexer_errors = get_lexer_and_tokens(input_data)
    
    # Si se encontraron errores léxicos, reportarlos y salir.
    if lexer_errors:
        for error in lexer_errors:
            print(error)
        sys.exit(1)

    # --------------------------------------------------------------------------
    # Definición del Analizador Sintáctico (Parser) y la Construcción del AST
    # --------------------------------------------------------------------------

    # Clases de Nodos del Árbol de Sintaxis Abstracta (AST).
    # Cada clase representa un tipo de construcción sintáctica del lenguaje.
    # Los nodos almacenan el operador de la construcción y sus hijos (sub-árboles).

    class Block():
        """Representa un bloque de código."""
        def __init__(self,op = None, leftson = None, rightson = None):
            self.op = op          # Operador o tipo de nodo (ej: "Block")
            self.leftson = leftson  # Hijo izquierdo del nodo
            self.rightson = rightson # Hijo derecho del nodo

    class DeclareSection(Block): 
        """Representa la sección de declaraciones dentro de un bloque."""
        pass
    class Sequencing(Block):
        """Representa una secuencia de instrucciones o declaraciones."""
        pass
    class SequencingDeclare(Block): 
        """Representa una secuencia de declaraciones específicas."""
        pass
    class Declare(Block): 
        """Representa una declaración individual (variable o función)."""
        pass
    class WriteFunction(Block): 
        """Representa la escritura de valores a parámetros de una función."""
        pass
    class Asig(Block): 
        """Representa una instrucción de asignación."""
        pass
    class If(Block): 
        """Representa una sentencia condicional 'if' con guardias."""
        pass
    class While(Block): 
        """Representa una sentencia de bucle 'while'."""
        pass
    class Literal(Block): 
        """Representa un valor literal (número, true, false)."""
        pass
    class Expr(Block): 
        """Clase base para expresiones."""
        pass
    class Binary_expressions(Block):
        """Representa una operación binaria (ej: suma, resta, AND, OR)."""
        pass
    class Ident(Block): 
        """Representa un identificador (nombre de variable o función)."""
        pass
    class String(Block):
        """Representa un literal de cadena de texto."""
        pass
    class UExpresson(Block): 
        """Representa una operación unaria (ej: negación, menos unario)."""
        pass
    class Print(Block): 
        """Representa una instrucción de impresión."""
        pass
    class Skip(Block): 
        """Representa una instrucción 'skip' (no-operación)."""
        pass
    class Guard(Block): 
        """Representa una cláusula de guardia (condición --> instrucción) dentro de un 'if'."""
        pass
    class Then(Block): 
        """Representa la parte 'then' de una cláusula de guardia o bucle while."""
        pass
    class TwoPoints(Block): 
        """Representa la expresión 'expr1:expr2' para acceso a funciones."""
        pass


    # Definición de la precedencia de operadores.
    # Las tuplas definen el nivel de precedencia (de menor a mayor) y la asociatividad.
    precedence = (
        ("left", "TkOr"),        # Or (menos precedencia)
        ("left", "TkAnd"),       # And
        ("left", "TkNEqual", "TkEqual"), # ==, <>
        ("left", "TkLeq", "TkLess", "TkGreater", "TkGeq"), # <=, <, >, >=
        ("left", "TkComma"),     # , (para listas de identificadores/expresiones)
        ("left", "TkTwoPoints"), # : (para acceso a funciones tipo (expr1:expr2))
        ("left", "TkPlus", "TkMinus"), # +, -
        ("left", "TkMult"),      # * (mayor precedencia para operadores aritméticos)
        ("right", "UMinus", "TkNot"), # !, - (unario, asociatividad derecha)
        ("left", "TkApp")        # . (para aplicación de función o acceso a miembros)
    )

    # Define el símbolo inicial de la gramática (la regla de producción de más alto nivel).
    start = "Block"

    # --------------------------------------------------------------------------
    # Reglas gramaticales para el parsing y construcción del AST
    # --------------------------------------------------------------------------
    # Cada función `p_` define una regla de producción.
    # La docstring de la función (`"""Rule : Production"""`) es la definición de la regla.
    # `p[0]` es el valor de la regla actual, `p[1]`, `p[2]`, etc., son los valores de los símbolos de su producción.

    def p_Block(p):
        """
        Block : TkOBlock DeclareSection Sequencing TkCBlock
        """
        # Representa un bloque de código con sección de declaraciones y secuencia de instrucciones.
        p[0] = Block("Block", p[2], p[3])

    def p_block_only_sequencing(p):
        """
        Block : TkOBlock Sequencing TkCBlock
        """
        # Representa un bloque de código solo con secuencia de instrucciones (sin declaraciones).
        p[0] = Block("Block", p[2]) # p[2] es la secuencia de instrucciones

    def p_sequencing(p):
        """
        Sequencing : Sequencing TkSemicolon Instruction
        """
        # Regla recursiva para una secuencia de instrucciones separadas por ';'.
        p[0] = Sequencing("Sequencing", p[1], p[3])

    def p_sequencing_only(p):
        """
        Sequencing : Instruction
        """
        # Caso base para una secuencia de una sola instrucción.
        p[0] = p[1] # El valor de la secuencia es el valor de la instrucción.

    def p_instruction(p):
        """
        Instruction : Asig
                    | While
                    | If
                    | Print
                    | Skip
                    | Block
        """
        # Define los tipos de instrucciones válidas en el lenguaje.
        p[0] = p[1]

    def p_declare_section(p):
        """
        DeclareSection : SequencingDeclare
        """
        # Define la sección de declaraciones, que es una secuencia de declaraciones.
        p[0] = DeclareSection("Declare", p[1])

    def p_sequencing_declare_recursivo(p):
        """
        SequencingDeclare : SequencingDeclare Declare TkSemicolon
        """
        # Regla recursiva para una secuencia de declaraciones terminadas en ';'.
        p[0] = SequencingDeclare("Sequencing", p[1], p[2])

    def p_sequencing_declare(p):
        """
        SequencingDeclare : Declare TkSemicolon
        """
        # Caso base para una secuencia de una sola declaración terminada en ';'.
        p[0] = p[1]

    def p_declare_int_bool(p):
        """
        Declare : TkBool TkId
                | TkInt TkId
        """
        # Regla para declarar una variable de tipo int o bool.
        p[0] = Declare(p[2] + " : " + p[1]) # Formato "id : tipo"

    def p_declare_function(p):
        """
        Declare : TkFunction TkOBracket TkSoForth Literal TkCBracket TkId
        """
        # Regla para declarar una función con un literal como tamaño.
        p[0] = Declare(p[6] + " : " + "function[.." + p[4].op + "]") # Formato "id : function[..literal]"

    def p_declare_int_bool_with_comma(p):
        """
        Declare : TkBool TkId Comma
                | TkInt TkId Comma
        """
        # Permite declarar múltiples variables del mismo tipo separadas por comas.
        p[0] = Declare(p[2] + p[3] + " : " + p[1])

    def p_declare_function_with_comma(p):
        """
        Declare : TkFunction TkOBracket TkSoForth Literal TkCBracket TkId Comma
        """
        # Permite declarar múltiples funciones separadas por comas.
        p[0] = Declare(p[6] + p[7] + " : " + "function[.." + p[4].op + "]")

    def p_comma(p):
        """
        Comma : TkComma TkId
        """
        # Regla para el patrón de una coma seguida de un identificador.
        p[0] = p[1] + " " + p[2]

    def p_comma_with_comma(p):
        """
        Comma : TkComma TkId Comma
        """
        # Regla recursiva para múltiples identificadores separados por comas.
        p[0] = p[1] + " " + p[2] +  p[3]

    def p_asig(p):
        """
        Asig : Ident TkAsig expression
        """
        # Regla para la instrucción de asignación.
        p[0] = Asig("Asig", p[1], p[3])

    def p_if(p):
        """
        If : TkIf Guard TkFi
        """
        # Regla para la sentencia 'if' con una o más guardias.
        p[0] = If("If", p[2])

    def p_guard0(p):
        """
        Guard : Guard TkGuard Then
        """
        # Regla recursiva para guardias anidadas (ej: [] condición --> instrucciones).
        p[0] = Guard("Guard", p[1], p[3])

    def p_guard1(p):
        """
        Guard : Then
        """
        # Caso base para una guardia (la primera en un 'if').
        p[0] = p[1] # El valor de la guardia es el valor del Then.

    def p_while(p):
        """
        While : TkWhile Then TkEnd
        """
        # Regla para el bucle 'while'.
        p[0] = While("While", p[2])

    def p_then(p):
        """
        Then : expression TkArrow Sequencing
        """
        # Regla para la cláusula 'then' de una guardia o un bucle 'while'.
        # Contiene una expresión de condición y una secuencia de instrucciones.
        p[0] = Then("Then",p[1], p[3])

    def p_skip(p):
        """
        Skip : TkSkip
        """
        # Regla para la instrucción 'skip'.
        p[0] = Skip("skip")

    def p_print(p):
        """
        Print : TkPrint expression
        """
        # Regla para la instrucción 'print'.
        p[0] = Print("Print", p[2])

    # Reglas para expresiones binarias (aritméticas, lógicas, de comparación, aplicación, acceso).
    # La precedencia y asociatividad se manejan con la tabla `precedence` y las reglas `terminoX`.
    def p_binary_expressions(p):
        """
        expression : expression TkOr termino0
        termino0 : termino0 TkAnd termino1
        termino1 : termino1 TkEqual termino12
                 | termino1 TkNEqual termino12
                 | termino1 TkLeq termino12
                 | termino1 TkLess termino12
                 | termino1 TkGeq termino12
                 | termino1 TkGreater termino12
        termino12 : termino12 TkComma termino2
                  | termino12 TkTwoPoints termino2
        termino2 : termino2 TkPlus termino3
                 | termino2 TkMinus termino3 
        termino3 : termino3 TkMult factor
        factor : factor TkApp factor
        """
        # Se mapea el token del operador a su nombre en el AST.
        if p[2] == "+":
            p[0] = Binary_expressions("Plus", p[1], p[3])
        elif p[2] == "-":
            p[0] = Binary_expressions("Minus", p[1], p[3])
        elif p[2] == "and":
            p[0] = Binary_expressions("And", p[1], p[3])
        elif p[2] == ".":
            p[0] = Binary_expressions("App", p[1], p[3])
        elif p[2] == "*":
            p[0] = Binary_expressions("Mult", p[1], p[3])
        elif p[2] == "or":
            p[0] = Binary_expressions("Or", p[1], p[3])
        elif p[2] == "==":
            p[0] = Binary_expressions("Equal", p[1], p[3])
        elif p[2] == "<>":
            p[0] = Binary_expressions("NotEqual", p[1], p[3])
        elif p[2] == "<=":
            p[0] = Binary_expressions("Leq", p[1], p[3])
        elif p[2] == "<":
            p[0] = Binary_expressions("Less", p[1], p[3])
        elif p[2] == ">=":
            p[0] = Binary_expressions("Geq", p[1], p[3])
        elif p[2] == ">":
            p[0] = Binary_expressions("Greater", p[1],p[3])
        elif p[2] == ",":
            p[0] = Binary_expressions("Comma", p[1], p[3])
        elif p[2] == ":":
            p[0] = Binary_expressions("TwoPoints", p[1], p[3])

    def p_unary_expression(p):
        """
        factor : TkNot factor
               | TkMinus factor %prec UMinus
        """
        # Reglas para expresiones unarias (negación lógica o menos unario).
        # `%prec UMinus` especifica la precedencia para el menos unario.
        if p[1] == "!":
            p[0] = UExpresson("Not", p[2])
        elif p[1] =="-":
            p[0] = UExpresson("Minus", p[2])
            
    def p_factor(p):
        """
        factor : TkOpenPar expression TkClosePar
        """
        # Agrupación de expresiones con paréntesis.
        p[0] = p[2] # El valor del factor es la expresión dentro de los paréntesis.

    def p_factor_writefunction(p):
        """
        factor : factor TkOpenPar expression TkClosePar
        """
        # Maneja la escritura de valores a parámetros de función (ej: `f(x)`).
        # Se interpreta como una operación de "WriteFunction" con el nombre de la función y la expresión de acceso.
        p[0] = Binary_expressions("WriteFunction", p[1], p[3])

    def p_subtitutions(p):
        """
        expression : termino0
        termino0 : termino1
        termino1 : termino12
        termino12 : termino2
        termino2 : termino3
        termino3 : termino4
        termino4 : factor
        factor : Literal
               | Ident
               | String
        """
        # Reglas de "sustitución" que permiten que una expresión de menor precedencia
        # sea tratada como una de mayor precedencia en el árbol de análisis.
        # Básicamente, pasan el valor del lado derecho al izquierdo.
        p[0] = p[1]

    def p_ident(p):
        """
        Ident : TkId
        """
        # Regla para los identificadores.
        p[0] = Ident("Ident: " + p[1]) # Almacena el identificador con un prefijo.

    def p_string(p):
        """
        String : TkString
        """
        # Regla para los literales de cadena.
        p[0] = String("String: "+f"\"{p[1]}\"") # Almacena la cadena con un prefijo y comillas.

    # Manejo de errores sintácticos.
    def p_literal(p):
        """
        Literal : TkNum
                | TkTrue
                | TkFalse
        """
        # Regla para los literales numéricos y booleanos.
        p[0] = Literal("Literal: " + str(p[1])) # Almacena el literal con un prefijo.

    def p_error(p):
        """
        Función de manejo de errores sintácticos.
        Se llama automáticamente por PLY cuando se encuentra un error de sintaxis.
        """
        if p:
            # Si hay un token en el punto del error, intenta dar información de línea y columna.
            column = p.lexpos - p.lexer.lexdata.rfind('\n', 0, p.lexpos)
            if column <= 0: # Ajustar para casos donde el token está al inicio de línea
                column = p.lexpos + 1
            print(f"Sintax error in row {p.lineno}, column {column}: unexpected token '{p.value}'")
        else:
            # Si el error es al final del archivo (EOF - End Of File)
            print("Syntax error at EOF")
        sys.exit(1) # Sale del programa indicando un error.

    # Construir el analizador sintáctico (parser).
    # Se inicializa el parser de PLY con las reglas de gramática y la tabla de precedencia.
    parser = Yacc.yacc()

    # Realiza el análisis sintáctico del contenido del archivo de entrada.
    result = parser.parse(input_data, lexer=lexer) # Pasa el lexer explícitamente al parser.

    # Imprime el Árbol de Sintaxis Abstracta (AST) si el análisis fue exitoso.
    if result:
        imprimir_ast(result, 0) # Llama a la función auxiliar para imprimir el AST.
    else:
        print("Parsing completado, pero no se generó AST (posiblemente por entrada vacía o errores de sintaxis).")


# --------------------------------------------------------------------------
# Funciones Auxiliares
# --------------------------------------------------------------------------

def imprimir_ast(arbol, n):
    """
    Función recursiva para imprimir el Árbol de Sintaxis Abstracta (AST).
    Recorre el árbol en preorden, imprimiendo el operador de cada nodo
    con una indentación que representa su nivel en el árbol.

    Args:
        arbol (Node): El nodo actual del AST a imprimir.
        n (int): El nivel de indentación actual.
    """
    current = arbol
    nivel = n

    if current != None:
        # Imprime el operador del nodo actual, con 'nivel' guiones para indentación.
        print("-" * nivel + f"{current.op}")
        
        # Llama recursivamente para el hijo izquierdo, aumentando el nivel de indentación.
        imprimir_ast(current.leftson, nivel + 1)
        
        # Llama recursivamente para el hijo derecho, aumentando el nivel de indentación.
        imprimir_ast(current.rightson, nivel + 1)


# Punto de entrada principal del script.
# Asegura que `main()` se ejecute solo cuando el script es ejecutado directamente.
if __name__ == "__main__":
    main()
