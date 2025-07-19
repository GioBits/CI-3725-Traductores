# Owner(s): Sergio Carrillo 14-11315 y David Pereira 18-10245
# Date: 15 de junio de 2025 (Actualizado)
# Description: Proyecto Etapa2 CI-3725 Traductores e Interpretadores -
#              Implementación de un analizador sintáctico para un lenguaje imperativo,
#              con construcción de un Árbol de Sintaxis Abstracta (AST),
#              utilizando el analizador léxico de lexer.py.

import ply.yacc as Yacc  # Importa el módulo Yacc de PLY para el analizador sintáctico
import sys               # Importa el módulo sys para acceder a argumentos de línea de comandos y salir del programa
from lexer import get_lexer_and_tokens, tokens # Importa la función para obtener el lexer y la lista de tokens


class Block():
    """Representa un bloque de código."""
    def __init__(self,op = None, leftson = None, rightson = None, value = None):
        self.op = op          # Operador o tipo de nodo (ej: "Block")
        self.leftson = leftson  # Hijo izquierdo del nodo
        self.rightson = rightson # Hijo derecho del nodo
        self.value = value
    def __str__(self):
        return f"{self.op}"

class DeclareSection():
    """Representa la sección de declaraciones dentro de un bloque."""
    def __init__(self,op = None, children = None):
        self.op = op          # Operador o tipo de nodo (ej: "Block")
        self.children = children
    def __str__(self):
        return f"{self.op}"

    def imprimir_declares(self, nivel):
        for son in self.children:
            tupla = son.VariableAndType
            for variale in tupla[1]:
                print("-" * nivel, f"variable: {variale} | type: {tupla[0]}", sep="")

                #print("-" * nivel, son, sep="")

class Sequencing(Block):
    """Representa una secuencia de instrucciones o declaraciones."""
    pass


class SequencingDeclare(Block):
    """Representa una secuencia de declaraciones específicas."""
    pass

class Declare():
    """Representa una declaración individual (variable o función)."""
    def __init__(self, op = None, VariableAndType = []):
        self.op = op
        self.VariableAndType = VariableAndType
        #self.VariableAndType[VariableAndType[0]] = VariableAndType[1]

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
class Literal():
    """Representa un valor literal (número, true, false)."""
    def __init__(self,op = None, value = None, type = None):
        self.op = op          # Operador o tipo de nodo (ej: "Block")
        self.value = value
        self.type = type
    def __str__(self):
        return f"Literal: {self.value} | type: {self.type}"
class Expr(Block):
    """Clase base para expresiones."""
    pass
class Binary_expressions():
    """Representa una operación binaria (ej: suma, resta, AND, OR)."""
    def __init__(self,op = None, leftson = None, rightson = None, type = None, number = None):
        self.op = op          # Operador o tipo de nodo (ej: "Block")
        self.leftson = leftson  # Hijo izquierdo del nodo
        self.rightson = rightson # Hijo derecho del nodo
        self.type = type
        self.number = number
    def __str__(self):
        if self.type != None:
            if self.op != "Comma":
                return f"{self.op} | type: {self.type}"
            else:
                return f"{self.op} | type: function with length={self.number}"
        else:
            return f"{self.op}"

class Ident():
    """Representa un identificador (nombre de variable o función)."""
    def __init__(self,op = None, value = None, type = None):
        self.op = op
        self.value = value        # Operador o tipo de nodo (ej: "Block")
        self.type = type
    def __str__(self):
        return f"Ident: {self.value} | type: {self.type}"

class String():
    """Representa un literal de cadena de texto."""
    def __init__(self,op = None, value = None, type = None):
        self.op = op
        self.value = value        # Operador o tipo de nodo (ej: "Block")
        self.type = type
    def __str__(self):
        return f"{self.op}"
class UExpresson():
    """Representa una operación unaria (ej: negación, menos unario)."""
    def __init__(self,op = None, leftson = None, rightson = None, type = None, number = None):
        self.op = op          # Operador o tipo de nodo (ej: "Block")
        self.leftson = leftson  # Hijo izquierdo del nodo
        self.rightson = rightson # Hijo derecho del nodo
        self.type = type
        self.number = number
    def __str__(self):
        if self.type != None:
            return f"{self.op} | type: {self.type}"
        else:
            return f"{self.op}"

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



    # Tabla de simbolos por alcance (scope)
    SymbolTableStack = [{}]

    # reportes de errores
    errores = []

    def lookup_symbol(var_name):
        """Looks up a symbol in the stack of scopes."""
        for scope in reversed(SymbolTableStack):
            if var_name in scope:
                return scope[var_name] # Returns {'type':..., 'line':...}
        return None

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

    def p_enter_scope(p):
        'enter_scope : '
        SymbolTableStack.append({})

    def p_block_only_sequencing(p):
        """
        Block : TkOBlock enter_scope Sequencing TkCBlock
        """
        # Representa un bloque de código solo con secuencia de instrucciones (sin declaraciones).
        # Creamos un DeclareSection vacío para que siempre se imprima "Symbols Table"
        empty_declare_section = DeclareSection("Symbols Table", [])
        p[0] = Block("Block", empty_declare_section, p[3])  # p[3] es la secuencia de instrucciones
        SymbolTableStack.pop()

    def p_Block(p):
        """
        Block : TkOBlock enter_scope DeclareSection Sequencing TkCBlock
        """
        # Representa un bloque de código con sección de declaraciones y secuencia de instrucciones.
        p[0] = Block("Block", p[3], p[4])
        SymbolTableStack.pop()

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
        p[0] = DeclareSection("Symbols Table", p[1])

    def p_sequencing_declare_recursivo(p):
        """
        SequencingDeclare : SequencingDeclare Declare TkSemicolon
        """
        # Regla recursiva para una secuencia de declaraciones terminadas en ';'.
        p[0] =  p[1] + [p[2]]

    def p_sequencing_declare(p):
        """
        SequencingDeclare : Declare TkSemicolon
        """
        # Caso base para una secuencia de una sola declaración terminada en ';'.
        p[0] = [p[1]]

    def p_declare_int_bool(p):
        """
        Declare : TkBool TkId
                | TkInt TkId
        """
        var_name = p[2]
        var_type = p[1]
        current_scope = SymbolTableStack[-1]

        if var_name in current_scope:
            original_line = current_scope[var_name]['line']
            error_msg = f"Variable {var_name} is already declared in the block at line {original_line}"
            errores.append(error_msg)
        else:
            line_num = p.lineno(2)
            current_scope[var_name] = {'type': var_type, 'line': line_num}

        p[0] = Declare(None, [var_type, [var_name]])

    def p_declare_function(p):
        """
        Declare : TkFunction TkOBracket TkSoForth factor TkCBracket TkId
        """
        var_name = p[6]
        current_scope = SymbolTableStack[-1]
        var_type = ""

        if isinstance(p[4], UExpresson):
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) +1
            if column <= 0: column = p.lexpos(2) + 1
            error_msg = f"Error: lower bound of the interval greater than the upper bound at line {line} and column {column}"
            errores.append(error_msg)
            var_type = "function[.." + p[4].leftson.value + "]"
        else:
            var_type = "function[.." + p[4].value + "]"

        if var_name in current_scope:
            original_line = current_scope[var_name]['line']
            error_msg = f"Variable {var_name} is already declared in the block at line {original_line}"
            errores.append(error_msg)
        else:
            line_num = p.lineno(6)
            current_scope[var_name] = {'type': var_type, 'line': line_num}

        p[0] = Declare(None, [var_type, [var_name]])

    def p_declare_int_bool_with_comma(p):
        """
        Declare : TkBool TkId Comma
                | TkInt TkId Comma
        """
        var_type = p[1]
        current_scope = SymbolTableStack[-1]
        
        # Procesa la primera variable y las siguientes de la regla Comma
        first_var_name = p[2]
        first_var_line = p.lineno(2)
        following_vars_with_lines = p[3] # Lista de tuplas (nombre, linea)
        
        all_vars_with_lines = [(first_var_name, first_var_line)] + following_vars_with_lines
        all_var_names = [name for name, line in all_vars_with_lines]

        for var_name, var_line in all_vars_with_lines:
            if var_name in current_scope:
                original_line = current_scope[var_name]['line']
                error_msg = f"Variable {var_name} is already declared in the block at line {original_line}"
                errores.append(error_msg)
            else:
                current_scope[var_name] = {'type': var_type, 'line': var_line}

        p[0] = Declare(None, [var_type, all_var_names])


    def p_declare_function_with_comma(p):
        """
        Declare : TkFunction TkOBracket TkSoForth factor TkCBracket TkId Comma
        """
        current_scope = SymbolTableStack[-1]
        var_type = ""

        if isinstance(p[4], UExpresson):
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) +1
            if column <= 0: column = p.lexpos(2) + 1
            error_msg = f"Error: lower bound of the interval greater than the upper bound at line {line} and column {column}"
            errores.append(error_msg)
            var_type = "function[.." + p[4].leftson.value + "]"
        else:
            var_type = "function[.." + p[4].value + "]"

        # Procesa la primera variable y las siguientes de la regla Comma
        first_var_name = p[6]
        first_var_line = p.lineno(6)
        following_vars_with_lines = p[7] # Lista de tuplas (nombre, linea)
        
        all_vars_with_lines = [(first_var_name, first_var_line)] + following_vars_with_lines
        all_var_names = [name for name, line in all_vars_with_lines]
        
        for var_name, var_line in all_vars_with_lines:
            if var_name in current_scope:
                original_line = current_scope[var_name]['line']
                error_msg = f"Variable {var_name} is already declared in the block at line {original_line}"
                errores.append(error_msg)
            else:
                current_scope[var_name] = {'type': var_type, 'line': var_line}

        p[0] = Declare( None, [var_type, all_var_names])

    def p_comma(p):
        """
        Comma : TkComma TkId
        """
        # Devuelve una lista con una tupla (nombre, numero_linea)
        var_name = p[2]
        line_num = p.lineno(2)
        p[0] = [(var_name, line_num)]

    def p_comma_with_comma(p):
        """
        Comma : TkComma TkId Comma
        """
        # Devuelve una lista de tuplas (nombre, numero_linea)
        var_name = p[2]
        line_num = p.lineno(2)
        p[0] = [(var_name, line_num)] + p[3]

    def p_asig(p):
        """
        Asig : Ident TkAsig expression
        """
        # The check for undeclared variables is now handled in p_ident.
        # This rule now only focuses on type checking for the assignment.
        if p[1].type is None:
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) -1-len(p[1].value)
            if column <= 0: # Ajuste para tokens al inicio de línea
                column = p.lexpos(2) + 1
            error_msg = f"Variable {p[1].value} not declared at line {line} and column {column}"
            errores[0] = error_msg
            # An "undeclared variable" error has already been logged by p_ident.
            # We can either stop or create a node and let further errors be caught.
            # Creating the node is often better for finding more errors in one go.
            pass

        if p[1].type == p[3].type or (p[1].type == "function[..0]" and p[3].type== "int"):
            p[0] = Asig("Asig", p[1], p[3])
        elif p[1].type != None and p[3].type != None and p[1].type.startswith("function") and p[3].type.startswith("function") and p[1].type[11] != p[3].type[11]:
            # Obtener la posición del token de asignación (:=) que es más confiable
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) +1
            if column <= 0: # Ajuste para tokens al inicio de línea
                column = p.lexpos(2) + 1

            error_msg = f"It is expected a list of length {int(p[1].type[11])+1} at line {line} and column {column}"
            errores.append(error_msg)
            p[0] = Asig("Asig", p[1], p[3])

        elif p[1].type != p[3].type and p[3].op != None and p[3].type != None and p[3].type.startswith("function") and p[3].op.startswith("WriteFunction"):
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) -1-(len(p[1].value))
            if column <= 0: # Ajuste para tokens al inicio de línea
                column = p.lexpos(2) + 1

            error_msg = f"Variable {p[1].value} is expected to be a function at line {line} and column {column}"
            errores.append(error_msg)
            p[0] = Asig("Asig", p[1], p[3])

        elif p[1].type is not None and p[3].type is not None and p[1].type != p[3].type:
            # Obtener la posición del token de asignación (:=) que es más confiable
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) -1-(len(p[1].value))
            if column <= 0: # Ajuste para tokens al inicio de línea
                column = p.lexpos(2) + 1

            error_msg = f"Type error. Variable {p[1].value} has different type than expression at line {line} and column {column}"
            errores.append(error_msg)
            p[0] = Asig("Asig", p[1], p[3])
        else:
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
        if p[1].type == "bool":
            p[0] = Then("Then",p[1], p[3])
        else:
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
            if column <= 0: # Ajuste para tokens al inicio de línea
                column = p.lexpos(2) + 1


            error_msg = f"No boolean guard at line {line} and column {column}"
            errores.append(error_msg)
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
            if p[1].type == "int" and p[3].type == "int":
                p[0] = Binary_expressions("Plus", p[1], p[3], "int")
            elif p[1].type == "String" and p[3].type == "String":
                p[0] = Binary_expressions("Concat", p[1], p[3], "String")
            elif (p[1].type == "bool" and p[3].type == "int") or (p[1].type == "int" and p[3].type == "bool") or (p[1].type == "bool" and p[3].type == "bool"):
                # Casos explícitos que deben dar error
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0:
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
                p[0] = Binary_expressions("Plus", p[1], p[3], None)
            else:
                # Para otros casos, fuerza la concatenación
                p[0] = Binary_expressions("Concat", p[1], p[3], "String")
        elif p[2] == "-":
            if p[1].type != "int" or p[3].type != "int":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("Minus", p[1], p[3], "int")
        elif p[2] == "and":

            if p[1].type != "bool" or p[3].type != "bool":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)


            p[0] = Binary_expressions("And", p[1], p[3], "bool")
        elif p[2] == ".":
            if isinstance(p[1], Ident):
                if p[1].type is None or not p[1].type.startswith("function"):
                    # No es función: error de no indexable
                    line = p.lineno(2)
                    column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) - 1
                    if column <= 0:
                        column = p.lexpos(2) + 1
                    error_msg = f"Error. {p[1].value} is not indexable at line {line} and column {column}"
                    errores.append(error_msg)
                elif p[3].type != "int":
                    # Es función pero índice no es int: error de índice. Es luego del operador indexador . que está el error
                    line = p.lineno(2)
                    column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) + 1
                    if column <= 0:
                        column = p.lexpos(2) + 1
                    error_msg = f"Error. Not integer index for function at line {line} and column {column}"
                    errores.append(error_msg)
            p[0] = Binary_expressions("ReadFunction", p[1], p[3], "int")
        elif p[2] == "*":
            if p[1].type != "int" or p[3].type != "int":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("Mult", p[1], p[3], "int")
        elif p[2] == "or":
            if p[1].type != "bool" or p[3].type != "bool":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("Or", p[1], p[3], "bool")
        elif p[2] == "==":
            if p[1].type == "int" and p[1].type == p[3].type : pass
            elif p[1].type == "bool" and p[1].type == p[3].type: pass
            else:
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("Equal", p[1], p[3], "bool")
        elif p[2] == "<>":
            #print(p[1].value, p[1].type)
            #print(p[3].value, p[3].type)
            if p[1].type == "int" and p[1].type == p[3].type : pass
            elif p[1].type == "bool" and p[1].type == p[3].type: pass
            else:
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("NotEqual", p[1], p[3], "bool")
        elif p[2] == "<=":
            if p[1].type != "int" or p[3].type != "int":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("Leq", p[1], p[3], "bool")
        elif p[2] == "<":
            if p[1].type != "int" or p[3].type != "int":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("Less", p[1], p[3], "bool")
        elif p[2] == ">=":
            if p[1].type != "int" or p[3].type != "int":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("Geq", p[1], p[3], "bool")
        elif p[2] == ">":
            if p[1].type != "int" or p[3].type != "int":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Type error at line {line} and column {column}"
                errores.append(error_msg)
            p[0] = Binary_expressions("Greater", p[1],p[3], "bool")
        elif p[2] == ",":
            if p[1].op =="Comma":
                if p[3].type != "int":
                    line = p.lineno(2)
                    column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                    if column <= 0: # Ajuste para tokens al inicio de línea
                        column = p.lexpos(2) + 1
                    error_msg = f"There is no integer list at line {line} and column {column}"
                    errores.append(error_msg)
                p[0] = Binary_expressions("Comma", p[1], p[3], f"function[..{p[1].number}]", p[1].number+1) # tener cuidado con el largo de las comas
            else:
                if p[3].type != "int" or p[1].type != "int":
                    line = p.lineno(2)
                    column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
                    if column <= 0: # Ajuste para tokens al inicio de línea
                        column = p.lexpos(2) + 1
                    error_msg = f"There is no integer list at line {line} and column {column}"
                    errores.append(error_msg)
                p[0] = Binary_expressions("Comma", p[1], p[3], f"function[..{1}]", 2)


        elif p[2] == ":":
            if p[1].type == "int" and p[3].type == "int":
                p[0] = Binary_expressions("TwoPoints", p[1], p[3])

            elif p[1].type == "int" and p[3].type != "int":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) +1
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Expected expression of type int at line {line} and column {column}"
                errores.append(error_msg)
                p[0] = Binary_expressions("TwoPoints", p[1], p[3])

            elif p[1].type != "int" and p[3].type == "int":
                line = p.lineno(2)
                column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) -len(p[1].value)
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(2) + 1
                error_msg = f"Expected expression of type int at line {line} and column {column}"
                errores.append(error_msg)
                p[0] = Binary_expressions("TwoPoints", p[1], p[3])

    def p_unary_expression(p):
        """
        factor : TkNot factor
               | TkMinus factor %prec UMinus
        """
        # Reglas para expresiones unarias (negación lógica o menos unario).
        # `%prec UMinus` especifica la precedencia para el menos unario.
        if p[1] == "!":
            if p[2].type == "bool":
                p[0] = UExpresson("Not", p[2], type = "bool")
            else:
                line = p.lineno(1)
                column = p.lexpos(1) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(1))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(1) + 1
                error_msg = f"Type error in line {line} and column {column}"
                errores.append(error_msg)
                p[0] = UExpresson("Not", p[2], type = "bool")

        elif p[1] =="-":
            if p[2].type == "int":
                p[0] = UExpresson("Minus", p[2], type = "int")
            else:
                line = p.lineno(1)
                column = p.lexpos(1) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(1))
                if column <= 0: # Ajuste para tokens al inicio de línea
                    column = p.lexpos(1) + 1
                error_msg = f"Type error in line {line} and column {column}"
                errores.append(error_msg)

                p[0] = UExpresson("Minus", p[2], type = "int")


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
        if p[1].type and p[1].type.startswith("function"):
            p[0] = Binary_expressions("WriteFunction", p[1], p[3], p[1].type)
        else:
            # Calcular línea y columna correctamente
            line = p.lineno(2)  # línea del '('
            lexdata = p.lexer.lexdata
            last_newline = lexdata.rfind('\n', 0, p.lexpos(2))
            column = (p.lexpos(2) - last_newline) if last_newline >= 0 else (p.lexpos(2) + 1)

            # Extraer la línea completa para verificación
            next_newline = lexdata.find('\n', p.lexpos(2))
            current_line = lexdata[last_newline+1:next_newline] if next_newline >=0 else lexdata[last_newline+1:]

            error_msg = f"The function modification operator is use in not function variable at line {line} and column {column-1}"
            errores.append(error_msg)
            p[0] = Binary_expressions("WriteFunction", p[1], p[3], p[1].type)

    def p_subtitutions(p):
        """
        expression : termino0
        termino0 : termino1
        termino1 : termino12
        termino12 : termino2
        termino2 : termino3
        termino3 : factor
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
        var_name = p[1]
        symbol_info = lookup_symbol(var_name)

        if symbol_info is None:
            line = p.lineno(1)
            column = p.lexpos(1) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(1))
            if column <= 0: # Ajuste para tokens al inicio de línea
                column = p.lexpos(1) + 1
            error_msg = f"Variable not declared at line {line} and column {column}"
            if not any(f"Variable not declared" in e for e in errores):
                 errores.append(error_msg)
            p[0] = Ident(value=var_name, type=None)
        else:
            p[0] = Ident(value=var_name, type=symbol_info['type'])

    def p_string(p):
        """
        String : TkString
        """
        # Regla para los literales de cadena.
        p[0] = String("String: "+f"\"{p[1]}\"", type = "String") # Almacena la cadena con un prefijo y comillas.

    # Manejo de errores sintácticos.
    def p_literal_num(p):
        """
        Literal : TkNum
        """
        # Regla para los literales numéricos y booleanos.
        p[0] = Literal(None, value=str(p[1]), type="int") # Almacena el literal con un prefijo.

    def p_literal_bool(p):
        """
        Literal : TkTrue
                | TkFalse
        """
        # Regla para los literales numéricos y booleanos.
        p[0] = Literal(None, value=str(p[1]), type = "bool") # Almacena el literal con un prefijo.

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
        if not errores:
            
            ## aquí comienza la salida de la etapa 4
            basicos = """
Z = lambda g:(lambda x:g(lambda v:x(x)(v)))(lambda x:g(lambda v:x(x)(v)))
true = lambda x:lambda y:x
false = lambda x:lambda y:y
nil = lambda x:true
cons = lambda x:lambda y:lambda f: f(x)(y)
head = lambda p: p(true)
tail = lambda p:p(false)
apply = Z(lambda g:lambda f:lambda x:f if x==nil else (g(f(head(x)))(tail(x))))
lift_do=lambda exp:lambda f:lambda g: lambda x: g(f(x)) if (exp(x)) else x
do=lambda exp:lambda f:Z(lift_do(exp)(f))
            """
            nombre = sys.argv[1].split('.')[0]
            with open(f"{nombre}.py", "w") as Salida:
                Salida.write(basicos)









        else:
            # Imprime el primer error encontrado para mantener la consistencia
            print(errores[0])
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


        if isinstance(current, DeclareSection):
            print("-" * nivel + f"{current.op}")
            current.imprimir_declares(nivel+1)

        elif isinstance(current, UExpresson):
            print("-" * nivel,current, sep="")
            # Llama recursivamente para el hijo izquierdo, aumentando el nivel de indentación.
            imprimir_ast(current.leftson, nivel + 1)

            # Llama recursivamente para el hijo derecho, aumentando el nivel de indentación.
            imprimir_ast(current.rightson, nivel + 1)

        elif isinstance(current, Binary_expressions):
            print("-" * nivel,current, sep="")
            # Llama recursivamente para el hijo izquierdo, aumentando el nivel de indentación.
            imprimir_ast(current.leftson, nivel + 1)

            # Llama recursivamente para el hijo derecho, aumentando el nivel de indentación.
            imprimir_ast(current.rightson, nivel + 1)

        elif isinstance(current, Literal):
            print("-" * nivel,current, sep="")
        elif isinstance(current, Ident):
            print("-" * nivel,current, sep="")
        elif isinstance(current, String):
            print("-" * nivel,current, sep="")
        else:
            print("-" * nivel + f"{current.op}")
            # Llama recursivamente para el hijo izquierdo, aumentando el nivel de indentación.
            imprimir_ast(current.leftson, nivel + 1)

            # Llama recursivamente para el hijo derecho, aumentando el nivel de indentación.
            imprimir_ast(current.rightson, nivel + 1)


# Punto de entrada principal del script.
# Asegura que `main()` se ejecute solo cuando el script es ejecutado directamente.
if __name__ == "__main__":
    main()
