# Owner(s): Sergio Carrillo 14-11315 y David Pereira 18-10245
# Date: June 11, 2025 (Updated)
# Description: Proyecto Etapa2 CI-3725 Traductores e Interpretadores -
#              Implementación de generación de AST y mejora de reglas de parsing para anidación de Guards.

import ply.yacc as Yacc
import ply.lex as Lex
import sys


# ------------------------------------------------
# Clases de Nodos AST
# ------------------------------------------------

class Node:
    """Clase base para todos los nodos del AST."""
    def __str__(self, level=0):
        # __str__ genérico para nodos sin hijos específicos para representación básica
        return "-" * level + self.__class__.__name__ + "\n"

class BlockNode(Node):
    """Representa un bloque de código, incluyendo declaraciones e instrucciones."""
    def __init__(self, declarations=None, instructions=None):
        self.declarations = declarations  # Un DeclarationsSectionNode
        self.instructions = instructions  # Puede ser un solo InstructionNode o un SequencingNode

    def __str__(self, level=0):
        ret = "-" * level + "Block\n"
        current_level = level + 1
        if self.declarations:
            ret += self.declarations.__str__(current_level)
        
        if self.instructions:
            # Aquí ya no asumimos que self.instructions es necesariamente un SequencingNode
            ret += self.instructions.__str__(current_level)
        return ret

class DeclarationsSectionNode(Node):
    """Representa toda la sección de declaraciones, conteniendo una secuencia de declaraciones."""
    def __init__(self, content_node): # Renombramos a content_node
        self.content_node = content_node

    def __str__(self, level=0):
        ret = "-" * level + "Declare\n"
        ret += self.content_node.__str__(level + 1) # Imprime el nodo contenido (SequencingNode o DeclareNode)
        return ret

class SequencingNode(Node):
    """Representa una secuencia de declaraciones o instrucciones."""
    def __init__(self, statements):
        self.statements = statements if statements is not None else []

    def __str__(self, level=0):
        ret = "-" * level + "Sequencing\n"
        current_level = level + 1
        for stmt in self.statements:
            ret += stmt.__str__(current_level)
        return ret

class DeclareNode(Node):
    """Representa una declaración de variable entera o booleana (ej: int a, b;)."""
    def __init__(self, identifiers, type_node):
        self.identifiers = identifiers  # Lista de objetos IdentNode
        self.type_node = type_node      # Objeto IntType o BoolType

    def __str__(self, level=0):
        id_names = ", ".join([ident.value for ident in self.identifiers])
        type_name = self.type_node.name # IntType.name o BoolType.name
        return "-" * level + f"{id_names} : {type_name}\n"

class FunctionDeclareNode(Node):
    """Representa una declaración de función (ej: function[..2] A;)."""
    def __init__(self, identifier, literal_node):
        self.identifier = identifier  # IdentNode
        self.literal = literal_node   # LiteralNode para el número

    def __str__(self, level=0):
        literal_str = self.literal.__str__(0).strip().replace("Literal: ", "") # Elimina "Literal: " para salida más limpia
        return "-" * level + f"{self.identifier.value} : function[..Literal: {literal_str}]\n"

class IntType(Node):
    """Representa el tipo 'int'."""
    def __init__(self):
        self.name = "int"
    def __str__(self, level=0):
        return self.name

class BoolType(Node):
    """Representa el tipo 'bool'."""
    def __init__(self):
        self.name = "bool"
    def __str__(self, level=0):
        return self.name

class AssignmentNode(Node):
    """Representa una asignación (ej: x := 5;)."""
    def __init__(self, target, value):
        self.target = target # IdentNode o AppNode (para asignación de elemento de array/función)
        self.value = value   # Nodo Expression

    def __str__(self, level=0):
        ret = "-" * level + "Asig\n"
        ret += self.target.__str__(level + 1)
        ret += self.value.__str__(level + 1)
        return ret

class IfNode(Node):
    """Representa una sentencia 'if' con múltiples guards."""
    # Ahora recibe una lista completa de GuardNode objetos
    def __init__(self, guards_list):
        self.guards_list = guards_list if guards_list is not None else []

    def __str__(self, level=0):
        ret = "-" * level + "If\n"
        current_level = level + 1 # Este será el nivel para '--Guard'

        num_total_guards = len(self.guards_list)
        
        # Imprimir la cadena de 'Guard's para establecer la anidación.
        # Se imprimen N-1 'Guard's para un total de N guardias, como en la salida esperada (5 para 6 guardias).
        num_guard_labels_to_print = num_total_guards - 1 

        # Asegurarse de no intentar imprimir un número negativo de guardias si num_total_guards es 0 o 1
        num_guard_labels_to_print = max(0, num_guard_labels_to_print)

        for i in range(num_guard_labels_to_print):
            ret += "-" * (current_level + i) + "Guard\n"

        # Calcular el nivel de indentación para los bloques 'Then'.
        # El nivel para el primer Then es: nivel del 'If' + numero_de_guardias_impresas + 1 (1 + 5 + 1 = 7)
        # Los subsiguientes Then decrementan su nivel por 1.
        
        # Calcular el nivel inicial del primer 'Then' (que será el más profundo)
        # Si 'level' es 0 para el "Block", entonces 'If' es 'level + 1' (1 guión).
        # El primer Guard es 'level + 1' (2 guiones).
        # El 'num_guard_labels_to_print' (5) representa los guiones *adicionales* a partir del '--Guard'.
        # Entonces, el '-------Then' tiene (level + 1) + num_guard_labels_to_print + 1 = 0 + 1 + 5 + 1 = 7 guiones.
        initial_then_level = level + num_guard_labels_to_print + 1 # This calculates 7 for the first 'Then'

        # Imprimir cada bloque 'Then' con la indentación decreciente
        for j, guard_node in enumerate(self.guards_list):
            then_level = initial_then_level - j # Decrementa el nivel por cada 'Then' subsiguiente
            
            then_node = ThenNode(guard_node.condition, guard_node.instruction_list)
            ret += then_node.__str__(then_level)
            
        return ret

class GuardNode(Node):
    """Representa un guard dentro de un 'if' (condición --> instrucción).
       Este nodo ahora solo almacena la condición y las instrucciones;
       su método __str__ solo imprime la etiqueta 'Guard'.
       La impresión del 'Then' correspondiente se maneja centralmente en IfNode.
    """
    def __init__(self, condition, instruction_list):
        self.condition = condition 
        self.instruction_list = instruction_list 

    def __str__(self, level=0):
        # NOTA: En esta configuración, solo se imprime la etiqueta 'Guard'.
        # El ThenNode asociado a este guard será impreso por IfNode.
        return "-" * level + "Guard\n"

class ThenNode(Node):
    """Representa la rama 'then' de un guard o while loop."""
    def __init__(self, condition_expr, instruction_list):
        self.condition_expr = condition_expr
        self.instruction_list = instruction_list
    def __str__(self, level=0):
        ret = "-" * level + "Then\n"
        ret += self.condition_expr.__str__(level + 1) # Imprime la condición
        ret += self.instruction_list.__str__(level + 1) # Imprime la lista de instrucciones
        return ret

class WhileNode(Node):
    """Representa un loop 'while'."""
    def __init__(self, condition, body):
        self.condition = condition # Nodo Expression
        self.body = body         # Nodo InstructionList

    def __str__(self, level=0):
        ret = "-" * level + "While\n"
        # While loop's condition and body are now handled by ThenNode for consistency
        ret += ThenNode(self.condition, self.body).__str__(level + 1)
        return ret

class PrintNode(Node):
    """Representa una sentencia 'print'."""
    def __init__(self, expression):
        self.expression = expression # Nodo Expression

    def __str__(self, level=0):
        ret = "-" * level + "Print\n"
        ret += self.expression.__str__(level + 1)
        return ret

class SkipNode(Node):
    """Representa una sentencia 'skip'."""
    def __init__(self):
        pass # No need for any attributes
    def __str__(self, level=0):
        return "-" * level + "Skip\n"

class BinaryOpNode(Node):
    """Representa una operación binaria (ej: a + b, x and y)."""
    def __init__(self, op, left, right):
        self.op = op # String del operador (ej: 'and', '<', '+')
        self.left = left
        self.right = right

    def __str__(self, level=0):
        # Mapea operadores simbólicos a sus nombres en AST para visualización
        op_map = {
            '<' : 'Less',
            '<=': 'Leq',
            '>' : 'Greater',
            '>=': 'Geq',
            '==': 'Equal',
            '<>': 'NotEqual', # Corregido de NEqual para consistencia
            '+' : 'Plus',
            '-' : 'Minus',
            '*' : 'Mult',
            'and': 'And', 
            'or': 'Or',
            '!': 'Not' 
        }
        display_op = op_map.get(self.op, self.op) # Usa el operador original si no está en el mapa
        ret = "-" * level + display_op + "\n"
        ret += self.left.__str__(level + 1)
        ret += self.right.__str__(level + 1)
        return ret

class UnaryOpNode(Node):
    """Representa una operación unaria (ej: !x, -y)."""
    def __init__(self, op, operand):
        self.op = op # String del operador (ej: 'not', 'minus')
        self.operand = operand

    def __str__(self, level=0):
        op_map = {
            '!' : 'Not',
            '-' : 'Minus'
        }
        display_op = op_map.get(self.op, self.op).capitalize()
        ret = "-" * level + display_op + "\n"
        ret += self.operand.__str__(level + 1)
        return ret

class LiteralNode(Node):
    """Representa un literal numérico, true o false."""
    def __init__(self, value):
        self.value = value

    def __str__(self, level=0):
        if isinstance(self.value, bool):
            return "-" * level + f"Literal: {str(self.value).lower()}\n" # Asegura minúsculas para booleanos
        return "-" * level + f"Literal: {self.value}\n"

class StringNode(Node):
    """Representa un literal de string."""
    def __init__(self, value):
        self.value = value

    def __str__(self, level=0):
        return "-" * level + f"String: \"{self.value}\"\n"

class IdentNode(Node):
    """Representa un identificador (nombre de variable)."""
    def __init__(self, value):
        self.value = value

    def __str__(self, level=0):
        return "-" * level + f"Ident: {self.value}\n"

class AppNode(Node):
    """Representa aplicación de función o acceso a elemento de array/función (ej: A.0, y.i)."""
    def __init__(self, left, right):
        self.left = left   # IdentNode para el nombre de la función/array
        self.right = right # LiteralNode o IdentNode para el índice/argumento

    def __str__(self, level=0):
        ret = "-" * level + "App\n"
        ret += self.left.__str__(level + 1)
        ret += self.right.__str__(level + 1)
        return ret

class WriteFunctionNode(Node):
    """Representa escritura a parámetros de función, posiblemente encadenada (ej: x(0:a)(1:b))."""
    def __init__(self, function_ident, access_exprs):
        self.function_ident = function_ident # IdentNode para el nombre de la función
        self.access_exprs = access_exprs     # Lista de AccessExpressionNode

    def __str__(self, level=0):
        ret = "-" * level + "WriteFunction\n"
        ret += self.function_ident.__str__(level + 1)
        for acc_expr in self.access_exprs:
            ret += acc_expr.__str__(level + 1)
        return ret

class AccessExpressionNode(Node):
    """Representa una expresión de acceso a función (ej: (expr1:expr2))."""
    def __init__(self, expr1, expr2):
        self.expr1 = expr1 # Nodo Expression para el primer argumento
        self.expr2 = expr2 # Nodo Expression para el segundo argumento

    def __str__(self, level=0):
        ret = "-" * level + "TwoPoints\n"
        ret += self.expr1.__str__(level + 1)
        ret += self.expr2.__str__(level + 1)
        return ret


def main():
    # Verificar que se proporcionó un archivo como argumento
    if len(sys.argv) != 2:
        print("Error: Por favor proporcione un archivo .imperat como argumento")
        print("Uso: python parse.py archivo.imperat")
        sys.exit(1)

    # Verificar que el archivo tenga la extensión correcta
    if not sys.argv[1].endswith('.imperat'):
        print("Error: El archivo debe tener extensión .imperat")
        sys.exit(1)

    # Intentar abrir y leer el archivo
    try:
        with open(sys.argv[1], 'r') as file:
            input_data = file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {sys.argv[1]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
        sys.exit(1)

    # Palabras reservadas del lenguaje
    reserved = {
        "if" : "TkIf",
        "fi" : "TkFi",
        "end" : "TkEnd",
        "while" : "TkWhile",
        "or" : "TkOr",
        "bool" : "TkBool",
        "true" : "TkTrue",
        "false" : "TkFalse",
        "skip" : "TkSkip",
        "int" : "TkInt",
        "function" : "TkFunction",
        "print" : "TkPrint",
        "and" : "TkAnd"
    }

    tokens = [
        "TkOBlock" ,
        "TkCBlock" ,
        "TkSoForth" ,
        "TkComma" ,
        "TkOpenPar" ,
        "TkClosePar" ,
        "TkAsig" ,
        "TkSemicolon" ,
        "TkArrow" ,
        "TkGuard" ,
        "TkPlus" ,
        "TkMinus" ,
        "TkMult" ,
        "TkNot" ,
        "TkLess" ,
        "TkLeq" ,
        "TkGeq" ,
        "TkGreater" ,
        "TkEqual" ,
        "TkNEqual" ,
        "TkOBracket" ,
        "TkCBracket" ,
        "TkTwoPoints" , # Corregido de TkTowPoints
        "TkApp",
        "TkNum",
        "TkString",
        "TkId"

    ] + list(reserved.values())

    # Tokens simples (definiciones regex)
    t_TkOBlock = r"\{"
    t_TkCBlock = r"\}"
    t_TkSoForth = r"\.\."   # Corregido de "\. \."
    t_TkComma = r"\,"       
    t_TkOpenPar = r"\("
    t_TkClosePar = r"\)"
    t_TkAsig = r"\:\="
    t_TkSemicolon = r"\;"
    t_TkArrow = r"\-\-\>"
    t_TkGuard = r"\[\]"
    t_TkPlus = r"\+"
    t_TkMinus = r"\-"
    t_TkMult = r"\*"
    t_TkNot = r"\!"
    t_TkLess = r"\<"
    t_TkLeq = r"\<\="
    t_TkGeq = r"\>\="
    t_TkGreater = r"\>"
    t_TkEqual = r"\=\="
    t_TkNEqual = r"\<\>"
    t_TkOBracket = r"\["
    t_TkCBracket = r"\]"
    t_TkTwoPoints = r"\:" # Nombre corregido de TkTowPoints
    t_TkApp = r"\."

    # Tokens especiales
    def t_COMMENT(t):
        r'//.*'
        pass  # No retorna valor, ignora comentarios
        
    def t_TkId(t):
        r"[a-zA-Z_][a-zA-Z_0-9]*"
        t.type = reserved.get(t.value, "TkId")
        return t

    def t_TkString(t):
        r'"[^"\\\n]*(?:\\[n"\\][^"\\\n]*)*"'
        t.value = t.value[1:-1]  # Elimina comillas
        return t

    def t_TkNum(t):
        r"\d+"
        t.value = int(t.value)
        return t

    # Manejo de errores para el lexer
    errors = []  # Lista para almacenar errores léxicos

    def t_error(t):
        column = t.lexpos - t.lexer.lexdata.rfind('\n', 0, t.lexpos)
        if column <= 0: # Manejar casos donde el token está al inicio de la línea
            column = t.lexpos + 1
        errors.append(f"Error: Unexpected character \"{t.value[0]}\" in row {t.lineno}, column {column}")
        t.lexer.skip(1)

    # Token ignorado (espacios en blanco)
    t_ignore = " \t"

    # Seguimiento de número de línea
    def t_newline( t ):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # Construir el lexer
    lexer = Lex.lex()

    # Definir precedencia de operadores (de menor a mayor) y asociatividad
    precedence = (
        ("left", "TkOr"),
        ("left", "TkAnd"),
        ("left", "TkNEqual", "TkEqual", "TkLeq", "TkLess", "TkGreater", "TkGeq"),
        ("left", "TkPlus", "TkMinus"),
        ("left", "TkMult"),
        ("right", "UMinus", "TkNot")  # UMinus para menos unario
    )

    # Definir el símbolo inicial para la gramática
    start = "program"

    # Reglas gramaticales para parsing y construcción de AST
    
    def p_program(p):
        """
        program : Block
        """
        p[0] = p[1]

    def p_empty(p):
        """
        empty :
        """
        pass

    def p_Block(p):
        """
        Block : TkOBlock InnerBlock TkCBlock
        """
        p[0] = BlockNode(declarations=p[2][0], instructions=p[2][1])

    def p_InnerBlock(p):
        """
        InnerBlock : DeclareSection InstructionList
                   | DeclareSection
                   | InstructionList
                   | empty
        """
        declarations_node = None
        instructions_node = None

        if len(p) == 3: # DeclareSection InstructionList
            # p[1] es una lista de nodos de declaración (del p_DeclareSection modificado)
            if p[1]: # Si hay declaraciones
                if len(p[1]) == 1 and isinstance(p[1][0], DeclareNode):
                    # Si solo hay una declaración de tipo primitivo, el DeclarationsSectionNode
                    # contendrá directamente ese DeclareNode.
                    declarations_node = DeclarationsSectionNode(p[1][0])
                else:
                    # Si hay múltiples declaraciones o funciones, se agrupan en SequencingNode
                    declarations_node = DeclarationsSectionNode(SequencingNode(p[1]))
            instructions_node = p[2] # Este ya será un SequencingNode o el nodo Instruction
            p[0] = (declarations_node, instructions_node)

        elif len(p) == 2:
            if isinstance(p[1], list): # Es un DeclareSection (p[1] es una lista de nodos)
                if p[1]: # Si hay declaraciones
                    if len(p[1]) == 1 and isinstance(p[1][0], DeclareNode):
                        declarations_node = DeclarationsSectionNode(p[1][0])
                    else:
                        declarations_node = DeclarationsSectionNode(SequencingNode(p[1]))
                p[0] = (declarations_node, None)
            else: # Debe ser un InstructionList
                p[0] = (None, p[1])
        else: # empty
            p[0] = (None, None)

    def p_DeclarationGroup_primitive(p):
        """
        DeclarationGroup : Type IdentList
        """
        p[0] = DeclareNode(p[2], p[1])

    def p_DeclarationGroup_function(p):
        """
        DeclarationGroup : FunctionDeclaration
        """
        p[0] = p[1] # p[1] es ya un SequencingNode de FunctionDeclareNode

    def p_DeclareSection(p):
        """
        DeclareSection : DeclarationGroup TkSemicolon
                       | DeclarationGroup TkSemicolon DeclareSection
        """
        if len(p) == 3: # Caso base: un solo grupo de declaración
            # Siempre retorna una lista, incluso si es de un solo elemento
            # Si p[1] es un SequencingNode (para funciones), aplanamos sus statements
            if isinstance(p[1], SequencingNode):
                p[0] = p[1].statements
            else: # Es un DeclareNode (variable primitiva)
                p[0] = [p[1]]
        else: # Caso recursivo: múltiples grupos de declaración
            current_group_list = []
            if isinstance(p[1], SequencingNode): # Si es una función, aplanamos
                current_group_list = p[1].statements
            else: # Es una variable primitiva
                current_group_list = [p[1]]

            p[0] = current_group_list + p[3] # p[3] ya será una lista de la recursión
    
    def p_InstructionList(p):
        """
        InstructionList : Instruction
                        | Instruction TkSemicolon InstructionList
        """
        if len(p) == 2: # Instrucción única
            # Directamente el nodo de instrucción, sin SequencingNode si es uno solo
            p[0] = p[1]
        else: # Caso recursivo: múltiples instrucciones
            current_instruction = p[1]
            rest_of_list = p[3] # Esto puede ser un nodo de instrucción o un SequencingNode

            if isinstance(rest_of_list, SequencingNode):
                # Si el resto de la lista ya es un SequencingNode, añadimos la instrucción actual al principio
                p[0] = SequencingNode([current_instruction] + rest_of_list.statements)
            else:
                # Si el resto de la lista es una única instrucción, creamos un nuevo SequencingNode
                # que contenga la instrucción actual y la siguiente.
                p[0] = SequencingNode([current_instruction, rest_of_list])

    def p_instruction(p):
        """
        Instruction : Assignment
                    | WhileLoop
                    | IfStatement
                    | PrintStatement
                    | SkipStatement
                    | Block
        """
        p[0] = p[1]

    def p_function_declaration(p):
        """
        FunctionDeclaration : TkFunction TkOBracket TkSoForth Literal TkCBracket IdentList
        """
        func_declarations = []
        for ident_node in p[6]:
            func_declarations.append(FunctionDeclareNode(ident_node, p[4]))
        p[0] = SequencingNode(func_declarations)

    def p_type(p):
        """
        Type : TkInt
             | TkBool
        """
        if p[1] == "int":
            p[0] = IntType()
        else: # p[1] == "bool"
            p[0] = BoolType()

    def p_ident_list(p):
        """
        IdentList : Ident
                  | Ident TkComma IdentList
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_assignment(p):
        """
        Assignment : Ident TkAsig Expression
                   | Ident TkAsig WriteFunction
                   | AppExpression TkAsig Expression
        """
        p[0] = AssignmentNode(p[1], p[3])

    def p_write_function(p):
        """
        WriteFunction : Ident AccessExpressionList
        """
        p[0] = WriteFunctionNode(p[1], p[2])

    def p_access_expression_list(p):
        """
        AccessExpressionList : AccessExpression
                             | AccessExpression AccessExpressionList
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_access_expression(p):
        """
        AccessExpression : TkOpenPar Expression TkTwoPoints Expression TkClosePar
        """
        p[0] = AccessExpressionNode(p[2], p[4])

    def p_if_statement(p):
        """
        IfStatement : TkIf FirstGuard OptGuards TkFi
        """
        # p[2] es el primer GuardNode (corresponde a la primera condición --> instrucciones)
        # p[3] es la lista de GuardNode objetos para los guards subsiguientes (los '[]')
        
        all_guards = [p[2]] # Start with the first guard
        if p[3]:
            all_guards.extend(p[3]) # Add subsequent guards if they exist
        
        p[0] = IfNode(all_guards)

    def p_first_guard(p):
        """
        FirstGuard : Expression TkArrow InstructionList
        """
        p[0] = GuardNode(p[1], p[3])

    # --- REGLAS PARA OptGuards y OptGuardsList ---
    def p_opt_guards(p):
        """
        OptGuards : OptGuardsList
                  | empty
        """
        # OptGuardsList retorna una lista, empty retorna None (que IfNode convertirá a [])
        p[0] = p[1]

    def p_opt_guards_list(p):
        """
        OptGuardsList : TkGuard Guard
                      | TkGuard Guard OptGuardsList
        """
        if len(p) == 3: # TkGuard Guard
            p[0] = [p[2]] # p[2] es un GuardNode
        else: # TkGuard Guard OptGuardsList
            p[0] = [p[2]] + p[3] # p[3] ya es una lista de la recursión
    # --- FIN DE LAS REGLAS PARA OptGuards y OptGuardsList ---

    def p_guard(p):
        """
        Guard : Expression TkArrow InstructionList
        """
        # Se sigue creando un GuardNode con su condición e instrucciones,
        # pero su método __str__ NO las imprimirá directamente en este caso.
        p[0] = GuardNode(p[1], p[3]) 
    
    def p_while_loop(p):
        """
        WhileLoop : TkWhile Expression TkArrow InstructionList TkEnd
        """
        p[0] = WhileNode(p[2], p[4])

    def p_print_statement(p):
        """
        PrintStatement : TkPrint Expression
        """
        p[0] = PrintNode(p[2])

    def p_skip_statement(p):
        """
        SkipStatement : TkSkip
        """
        p[0] = SkipNode()

    # Reglas de parsing de expresiones usando precedencia definida
    def p_expression_binary(p):
        """
        Expression : Expression TkOr AndExpression
        AndExpression : AndExpression TkAnd Comparison
        Comparison : Comparison TkEqual Sum
                   | Comparison TkNEqual Sum
                   | Comparison TkLess Sum
                   | Comparison TkLeq Sum
                   | Comparison TkGreater Sum
                   | Comparison TkGeq Sum
        Sum : Sum TkPlus Product
            | Sum TkMinus Product
        Product : Product TkMult Unary
        """
        # Pasa el valor crudo del token para el operador; el mapeo ocurrirá en __str__
        p[0] = BinaryOpNode(p[2], p[1], p[3]) 

    def p_expression_and_expression(p):
        """
        Expression : AndExpression
        AndExpression : Comparison
        Comparison : Sum
        Sum : Product
        Product : Unary
        """
        p[0] = p[1]

    def p_unary_expression(p):
        """
        Unary : TkNot Unary
              | TkMinus Unary %prec UMinus
              | Primary
        """
        if len(p) == 2: # Primary
            p[0] = p[1]
        else: # Operador unario, pasa el valor crudo del token
            p[0] = UnaryOpNode(p[1], p[2])

    def p_primary(p):
        """
        Primary : Literal
                | Ident
                | String
                | TkOpenPar Expression TkClosePar
                | AppExpression
                | WriteFunction
        """
        if len(p) == 2:
            p[0] = p[1]
        else: # TkOpenPar Expression TkClosePar
            p[0] = p[2]
    
    def p_app_expression_literal(p):
        """
        AppExpression : Ident TkApp Literal
        """
        p[0] = AppNode(p[1], p[3])

    def p_app_expression_ident(p):
        """
        AppExpression : Ident TkApp Ident
        """
        p[0] = AppNode(p[1], p[3])

    def p_literal(p):
        """
        Literal : TkNum
                | TkTrue
                | TkFalse
        """
        if isinstance(p[1], int):
            p[0] = LiteralNode(p[1])
        elif p[1] == 'true':
            p[0] = LiteralNode(True)
        elif p[1] == 'false':
            p[0] = LiteralNode(False)

    def p_ident(p):
        """
        Ident : TkId
        """
        p[0] = IdentNode(p[1])

    def p_string(p):
        """
        String : TkString
        """
        p[0] = StringNode(p[1])


    # Manejar errores sintácticos
    def p_error(p):
        if p:
            column = p.lexpos - p.lexer.lexdata.rfind('\n', 0, p.lexpos)
            if column <= 0: # Ajustar para casos donde el token está al inicio de línea
                column = p.lexpos + 1
            print(f"Sintax error in row {p.lineno}, column {column}: unexpected token '{p.value}'")
        else:
            print("Syntax error at EOF")
        sys.exit(1)


    # Construir el parser
    parser = Yacc.yacc()

    # Parsear los datos de entrada
    result = parser.parse(input_data)

    # Si se encontraron errores léxicos, reportarlos y salir
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    # Imprimir el AST si el parsing fue exitoso
    if result:
        print(result.__str__().strip()) # Usar el método __str__ del nodo raíz del AST
    else:
        print("Parsing completado, pero no se generó AST (posiblemente por entrada vacía o errores de sintaxis).")


if __name__ == "__main__":
    main()
