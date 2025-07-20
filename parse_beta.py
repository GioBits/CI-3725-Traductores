# Owner(s): Sergio Carrillo 14-11315 y David Pereira 18-10245
# Date: 20 de julio de 2025 (Corregido para Etapa 4)
# Description: Proyecto Etapa 4 CI-3725 Traductores e Interpretadores -
#              Implementación de un traductor de un lenguaje imperativo
#              a funciones Lambda en Python.

import ply.yacc as Yacc
import sys
# Se asume que lexer.py existe y contiene get_lexer_and_tokens y tokens
from lexer import get_lexer_and_tokens, tokens

# --------------------------------------------------------------------------
# Clases del Traductor a Lambda
# --------------------------------------------------------------------------

class LambdaTranslator:
    """
    Traduce un AST del lenguaje imperativo a una única función lambda en Python.
    Maneja los ámbitos, el estado (como una lista inmutable) y la semántica
    de traducción descrita en el enunciado del proyecto.
    """
    def __init__(self):
        # Pila para manejar ámbitos anidados.
        self.scope_stack = []
        # Lista ordenada de variables en el ámbito actual. El orden es crucial.
        self.current_vars_ordered = []
        # Mapa del nombre de la variable (ej: 'a') a su nombre en lambda (ej: 'x1').
        self.var_to_lambda_map = {}
        # Atributos para almacenar información del bloque principal para el archivo final
        self.main_block_vars = []
        self.main_block_defaults = []

    def enter_scope(self, declared_vars_list):
        """Entra en un nuevo ámbito, actualizando la lista de variables y el mapeo."""
        self.scope_stack.append((self.current_vars_ordered, self.var_to_lambda_map))
        
        # El nuevo ámbito incluye las variables anteriores más las nuevas.
        self.current_vars_ordered = self.current_vars_ordered + declared_vars_list
        
        new_map = {}
        for i, var_name in enumerate(self.current_vars_ordered):
            new_map[var_name] = f"x{i + 1}"
        self.var_to_lambda_map = new_map


    def exit_scope(self):
        """Sale del ámbito actual y restaura el anterior."""
        self.current_vars_ordered, self.var_to_lambda_map = self.scope_stack.pop()

    def get_lambda_var(self, var_name):
        """Obtiene el nombre de la variable lambda correspondiente a un nombre de variable."""
        return self.var_to_lambda_map.get(var_name, "VAR_NO_ENCONTRADA")

    def get_lambda_params_str(self):
        """Genera el string de parámetros para una función lambda en orden inverso (ej: 'lambda x3:lambda x2:lambda x1:')."""
        if not self.current_vars_ordered:
            return ""
        # La salida deseada requiere que los parámetros estén en orden inverso.
        params = [self.get_lambda_var(v) for v in reversed(self.current_vars_ordered)]
        return "lambda " + ":lambda ".join(params) + ":"

    def translate_expression(self, expr_node):
        """Traduce un nodo de expresión del AST a una cadena de expresión de Python."""
        if isinstance(expr_node, Literal):
            if expr_node.type == "bool":
                return "true" if expr_node.value == "True" else "false"
            return str(expr_node.value)

        elif isinstance(expr_node, Ident):
            return self.get_lambda_var(expr_node.value)

        elif isinstance(expr_node, Binary_expressions):
            left = self.translate_expression(expr_node.leftson)
            right = self.translate_expression(expr_node.rightson)
            
            op_map = {
                "Plus": "+", "Minus": "-", "Mult": "*",
                "And": " and ", "Or": " or ", "Equal": "==", "NotEqual": "!=",
                "Less": "<", "Leq": "<=", "Greater": ">", "Geq": ">="
            }
            if expr_node.op in op_map:
                # Se eliminan paréntesis innecesarios para que coincida con la salida deseada
                return f"{left}{op_map[expr_node.op]}{right}"
            
            if expr_node.op == "ReadFunction":
                return f"{left}[{right}]"
            
            if expr_node.op == "Comma":
                 if isinstance(expr_node.leftson, Binary_expressions) and expr_node.leftson.op == "Comma":
                     return f"{left[:-1]}, {right}]"
                 else:
                     return f"[{left}, {right}]"

        elif isinstance(expr_node, UExpresson):
            operand = self.translate_expression(expr_node.leftson)
            if expr_node.op == "Not":
                return f"(not {operand})"
            # FIX: Se corrige la traducción del operador unario Menos.
            if expr_node.op == "Minus":
                return f"-{operand}"
            
        return "ErrorExpr"

    def translate_assignment_body(self, asig_node):
        """Traduce el cuerpo de una asignación a una llamada 'apply(...)' sin aplicar al estado."""
        var_to_assign = asig_node.leftson.value
        expr_translation = self.translate_expression(asig_node.rightson)
        lambda_header = self.get_lambda_params_str()
        new_state_parts = []
        for var_name in self.current_vars_ordered:
            if var_name == var_to_assign:
                new_state_parts.append(expr_translation)
            else:
                new_state_parts.append(self.get_lambda_var(var_name))
        
        cons_chain = "nil"
        new_state_parts.reverse()
        # FIX: Para construir la lista cons(c)(cons(b)(cons(a)...)) se debe
        # iterar sobre las partes en el orden c, b, a.
        for part in new_state_parts:
            cons_chain = f"cons({part})({cons_chain})"
        
        # Se invierte el orden de construcción para que coincida con la salida deseada.
        new_state_parts.reverse()
        cons_chain = "nil"
        for part in new_state_parts:
            cons_chain = f"cons({part})({cons_chain})"

        return f"(apply({lambda_header}{cons_chain}))"


    def translate_if_lambda(self, if_node):
        """Traduce una instrucción 'if' a una función lambda completa que toma un estado."""
        guards_list = []
        current_node = if_node.leftson
        while isinstance(current_node, Guard):
            guards_list.append(current_node.rightson)
            current_node = current_node.leftson
        guards_list.append(current_node)
        guards_list.reverse()

        nested_else_branch = "x1"
        
        for then_node in reversed(guards_list):
            cond_expr_str = self.translate_expression(then_node.leftson)
            lambda_header = self.get_lambda_params_str()
            cond_function_call = f"apply({lambda_header}{cond_expr_str})(x1)"
            
            then_body_expression = self.translate_instruction(then_node.rightson, "x1")

            nested_else_branch = f"({then_body_expression} if {cond_function_call} else {nested_else_branch})"
            
        return f"(lambda x1: {nested_else_branch})"

    def translate_instruction(self, instruction_node, current_state_expr):
        """
        Traduce un nodo de instrucción a una cadena de expresión que representa el nuevo estado,
        aplicando la instrucción al estado de `current_state_expr`.
        """
        if isinstance(instruction_node, Asig):
            asig_func = self.translate_assignment_body(instruction_node)
            return f"({asig_func}({current_state_expr}))"

        elif isinstance(instruction_node, Sequencing):
            state_after_I1 = self.translate_instruction(instruction_node.leftson, current_state_expr)
            return self.translate_instruction(instruction_node.rightson, state_after_I1)

        elif isinstance(instruction_node, If):
            if_func = self.translate_if_lambda(instruction_node)
            return f"({if_func}({current_state_expr}))"

        elif isinstance(instruction_node, Block):
            block_func = self.translate_block(instruction_node)
            return f"({block_func}({current_state_expr}))"
        
        elif isinstance(instruction_node, (While, Print, Skip)):
            return current_state_expr
        
        return current_state_expr

    def get_default_value(self, var_type):
        """Obtiene el valor por defecto para un tipo de variable."""
        if var_type == "int":
            return "0"
        elif var_type == "bool":
            return "false"
        elif var_type.startswith("function"):
            try:
                size = int(var_type.split('..')[1][:-1]) + 1
                return str([0] * size)
            except (ValueError, IndexError):
                return "[]"
        return "None"

    def translate_block(self, block_node):
        """Traduce un bloque. Devuelve una función lambda completa (lambda x1: ...)."""
        is_main_block = not self.scope_stack

        declared_vars = []
        default_values = []
        if block_node.leftson and block_node.leftson.children:
            for declare_node in block_node.leftson.children:
                var_type = declare_node.VariableAndType[0]
                vars_list = declare_node.VariableAndType[1]
                declared_vars.extend(vars_list)
                for _ in vars_list:
                    default_values.append(self.get_default_value(var_type))

        self.enter_scope(declared_vars)

        # La traducción del cuerpo ahora es una expresión, no una lambda completa.
        # El estado inicial para el cuerpo del bloque es 'x1'.
        body_expression = self.translate_instruction(block_node.rightson, "x1")

        if is_main_block:
            self.main_block_vars = self.current_vars_ordered[:]
            self.main_block_defaults = default_values
            # La traducción final es la lambda para el bloque principal.
            final_translation = f"(lambda x1: {body_expression})"
        else:
            num_new_vars = len(declared_vars)
            
            initial_state_cons = "x1"
            for val in reversed(default_values):
                initial_state_cons = f"cons({val})({initial_state_cons})"
            
            body_expression_for_block = self.translate_instruction(block_node.rightson, initial_state_cons)
            
            tail_calls = "tail(" * num_new_vars
            
            final_translation = (f"(lambda x1: {tail_calls}"
                                 f"{body_expression_for_block}{')' * num_new_vars})")

        self.exit_scope()
        return final_translation

# --------------------------------------------------------------------------
# Clases del AST (sin cambios)
# --------------------------------------------------------------------------
class Block():
    def __init__(self,op = None, leftson = None, rightson = None, value = None):
        self.op = op; self.leftson = leftson; self.rightson = rightson; self.value = value
    def __str__(self): return f"{self.op}"

class DeclareSection():
    def __init__(self,op = None, children = None):
        self.op = op; self.children = children
    def __str__(self): return f"{self.op}"
    def imprimir_declares(self, nivel):
        for son in self.children:
            tupla = son.VariableAndType
            for variale in tupla[1]:
                print("-" * nivel, f"variable: {variale} | type: {tupla[0]}", sep="")

class Sequencing(Block): pass
class SequencingDeclare(Block): pass
class Declare():
    def __init__(self, op = None, VariableAndType = []):
        self.op = op; self.VariableAndType = VariableAndType
class WriteFunction(Block): pass
class Asig(Block): pass
class If(Block): pass
class While(Block): pass
class Literal():
    def __init__(self,op = None, value = None, type = None):
        self.op = op; self.value = value; self.type = type
    def __str__(self): return f"Literal: {self.value} | type: {self.type}"
class Expr(Block): pass
class Binary_expressions():
    def __init__(self,op = None, leftson = None, rightson = None, type = None, number = None):
        self.op = op; self.leftson = leftson; self.rightson = rightson; self.type = type; self.number = number
    def __str__(self):
        if self.type != None:
            if self.op != "Comma": return f"{self.op} | type: {self.type}"
            else: return f"{self.op} | type: function with length={self.number}"
        else: return f"{self.op}"
class Ident():
    def __init__(self,op = None, value = None, type = None):
        self.op = op; self.value = value; self.type = type
    def __str__(self): return f"Ident: {self.value} | type: {self.type}"
class String():
    def __init__(self,op = None, value = None, type = None):
        self.op = op; self.value = value; self.type = type
    def __str__(self): return f"{self.op}"
class UExpresson():
    def __init__(self,op = None, leftson = None, rightson = None, type = None, number = None):
        self.op = op; self.leftson = leftson; self.rightson = rightson; self.type = type; self.number = number
    def __str__(self):
        if self.type != None: return f"{self.op} | type: {self.type}"
        else: return f"{self.op}"
class Print(Block): pass
class Skip(Block): pass
class Guard(Block): pass
class Then(Block): pass
class TwoPoints(Block): pass

# --------------------------------------------------------------------------
# Función Principal y Lógica del Parser
# --------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print("Uso: python parse_ia.py archivo.imperat")
        sys.exit(1)
    if not sys.argv[1].endswith('.imperat'):
        print("Error: El archivo debe tener extensión .imperat")
        sys.exit(1)
    try:
        with open(sys.argv[1], 'r') as file:
            input_data = file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {sys.argv[1]}")
        sys.exit(1)

    lexer, lexer_tokens, lexer_errors = get_lexer_and_tokens(input_data)
    if lexer_errors:
        for error in lexer_errors: print(error)
        sys.exit(1)

    SymbolTableStack = [{}]
    errores = []

    def lookup_symbol(var_name):
        for scope in reversed(SymbolTableStack):
            if var_name in scope: return scope[var_name]
        return None

    precedence = (
        ("left", "TkOr"), ("left", "TkAnd"), ("left", "TkNEqual", "TkEqual"),
        ("left", "TkLeq", "TkLess", "TkGreater", "TkGeq"),
        ("left", "TkComma"), ("left", "TkTwoPoints"),
        ("left", "TkPlus", "TkMinus"), ("left", "TkMult"),
        ("right", "UMinus", "TkNot"), ("left", "TkApp")
    )
    start = "Block"

    def p_enter_scope(p):
        'enter_scope : '
        SymbolTableStack.append({})

    def p_block_only_sequencing(p):
        """
        Block : TkOBlock enter_scope Sequencing TkCBlock
        """
        empty_declare_section = DeclareSection("Symbols Table", [])
        p[0] = Block("Block", empty_declare_section, p[3])
        SymbolTableStack.pop()

    def p_Block(p):
        """
        Block : TkOBlock enter_scope DeclareSection Sequencing TkCBlock
        """
        p[0] = Block("Block", p[3], p[4])
        SymbolTableStack.pop()

    def p_sequencing(p):
        """
        Sequencing : Sequencing TkSemicolon Instruction
        """
        p[0] = Sequencing("Sequencing", p[1], p[3])

    def p_sequencing_only(p):
        """
        Sequencing : Instruction
        """
        p[0] = p[1]

    def p_instruction(p):
        """
        Instruction : Asig
                    | While
                    | If
                    | Print
                    | Skip
                    | Block
        """
        p[0] = p[1]

    def p_declare_section(p):
        """
        DeclareSection : SequencingDeclare
        """
        p[0] = DeclareSection("Symbols Table", p[1])

    def p_sequencing_declare_recursivo(p):
        """
        SequencingDeclare : SequencingDeclare Declare TkSemicolon
        """
        p[0] =  p[1] + [p[2]]

    def p_sequencing_declare(p):
        """
        SequencingDeclare : Declare TkSemicolon
        """
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
        
        first_var_name = p[2]
        first_var_line = p.lineno(2)
        following_vars_with_lines = p[3]
        
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

        first_var_name = p[6]
        first_var_line = p.lineno(6)
        following_vars_with_lines = p[7]
        
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
        var_name = p[2]
        line_num = p.lineno(2)
        p[0] = [(var_name, line_num)]

    def p_comma_with_comma(p):
        """
        Comma : TkComma TkId Comma
        """
        var_name = p[2]
        line_num = p.lineno(2)
        p[0] = [(var_name, line_num)] + p[3]

    def p_asig(p):
        """
        Asig : Ident TkAsig expression
        """
        if p[1].type is None:
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) -1-len(p[1].value)
            if column <= 0: column = p.lexpos(2) + 1
            error_msg = f"Variable {p[1].value} not declared at line {line} and column {column}"
            errores.append(error_msg)
            pass

        if p[1].type == p[3].type or (p[1].type == "function[..0]" and p[3].type== "int"):
            p[0] = Asig("Asig", p[1], p[3])
        elif p[1].type != None and p[3].type != None and p[1].type.startswith("function") and p[3].type.startswith("function") and p[1].type[11] != p[3].type[11]:
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) +1
            if column <= 0: column = p.lexpos(2) + 1
            error_msg = f"It is expected a list of length {int(p[1].type[11])+1} at line {line} and column {column}"
            errores.append(error_msg)
            p[0] = Asig("Asig", p[1], p[3])
        elif p[1].type != p[3].type and p[3].op != None and p[3].type != None and p[3].type.startswith("function") and p[3].op.startswith("WriteFunction"):
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) -1-(len(p[1].value))
            if column <= 0: column = p.lexpos(2) + 1
            error_msg = f"Variable {p[1].value} is expected to be a function at line {line} and column {column}"
            errores.append(error_msg)
            p[0] = Asig("Asig", p[1], p[3])
        elif p[1].type is not None and p[3].type is not None and p[1].type != p[3].type:
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2)) -1-(len(p[1].value))
            if column <= 0: column = p.lexpos(2) + 1
            error_msg = f"Type error. Variable {p[1].value} has different type than expression at line {line} and column {column}"
            errores.append(error_msg)
            p[0] = Asig("Asig", p[1], p[3])
        else:
            p[0] = Asig("Asig", p[1], p[3])

    def p_if(p):
        """ If : TkIf Guard TkFi """
        p[0] = If("If", p[2])

    def p_guard0(p):
        """ Guard : Guard TkGuard Then """
        p[0] = Guard("Guard", p[1], p[3])

    def p_guard1(p):
        """ Guard : Then """
        p[0] = p[1]

    def p_while(p):
        """ While : TkWhile Then TkEnd """
        p[0] = While("While", p[2])

    def p_then(p):
        """ Then : expression TkArrow Sequencing """
        if p[1].type == "bool":
            p[0] = Then("Then",p[1], p[3])
        else:
            line = p.lineno(2)
            column = p.lexpos(2) - p.lexer.lexdata.rfind('\n', 0, p.lexpos(2))
            if column <= 0: column = p.lexpos(2) + 1
            error_msg = f"No boolean guard at line {line} and column {column}"
            errores.append(error_msg)
            p[0] = Then("Then",p[1], p[3])

    def p_skip(p):
        """ Skip : TkSkip """
        p[0] = Skip("skip")

    def p_print(p):
        """ Print : TkPrint expression """
        p[0] = Print("Print", p[2])

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
        op_map = {
            "+": "Plus", "-": "Minus", "*": "Mult", "and": "And", "or": "Or",
            "==": "Equal", "<>": "NotEqual", "<=": "Leq", "<": "Less",
            ">=": "Geq", ">": "Greater", ",": "Comma", ":": "TwoPoints",
            ".": "ReadFunction"
        }
        op_name = op_map.get(p[2])
        
        type_result = None
        if op_name in ["Plus", "Minus", "Mult"]:
            if p[1].type != "int" or p[3].type != "int":
                errores.append(f"Type error at line {p.lineno(2)}")
            type_result = "int"
        elif op_name in ["And", "Or"]:
            if p[1].type != "bool" or p[3].type != "bool":
                errores.append(f"Type error at line {p.lineno(2)}")
            type_result = "bool"
        elif op_name in ["Equal", "NotEqual"]:
            if p[1].type != p[3].type:
                errores.append(f"Type error for {p[2]} at line {p.lineno(2)}")
            type_result = "bool"
        elif op_name in ["Leq", "Less", "Geq", "Greater"]:
            if p[1].type != "int" or p[3].type != "int":
                errores.append(f"Type error for {p[2]} at line {p.lineno(2)}")
            type_result = "bool"
        elif op_name == "ReadFunction":
            if not (p[1].type and p[1].type.startswith("function")):
                errores.append(f"Error: {p[1].value} is not indexable at line {p.lineno(2)}")
            if p[3].type != "int":
                errores.append(f"Error: Not integer index for function at line {p.lineno(2)}")
            type_result = "int"
        elif op_name == "Comma":
            if p[1].op == "Comma":
                p[0] = Binary_expressions("Comma", p[1], p[3], f"function[..{p[1].number}]", p[1].number+1)
            else:
                p[0] = Binary_expressions("Comma", p[1], p[3], f"function[..{1}]", 2)
            return

        p[0] = Binary_expressions(op_name, p[1], p[3], type_result)
        
    def p_unary_expression(p):
        """
        factor : TkNot factor
               | TkMinus factor %prec UMinus
        """
        if p[1] == "!":
            if p[2].type != "bool":
                errores.append(f"Type error at line {p.lineno(1)}")
            p[0] = UExpresson("Not", p[2], type="bool")
        elif p[1] == "-":
            if p[2].type != "int":
                errores.append(f"Type error at line {p.lineno(1)}")
            p[0] = UExpresson("Minus", p[2], type="int")

    def p_factor(p):
        """ factor : TkOpenPar expression TkClosePar """
        p[0] = p[2]

    def p_factor_writefunction(p):
        """ factor : factor TkOpenPar expression TkClosePar """
        if p[1].type and p[1].type.startswith("function"):
            p[0] = Binary_expressions("WriteFunction", p[1], p[3], p[1].type)
        else:
            errores.append(f"The function modification operator is used on a non-function variable at line {p.lineno(2)}")
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
        p[0] = p[1]

    def p_ident(p):
        """ Ident : TkId """
        var_name = p[1]
        symbol_info = lookup_symbol(var_name)
        if symbol_info is None:
            errores.append(f"Variable '{var_name}' not declared at line {p.lineno(1)}")
            p[0] = Ident(value=var_name, type=None)
        else:
            p[0] = Ident(value=var_name, type=symbol_info['type'])

    def p_string(p):
        """ String : TkString """
        p[0] = String("String: "+f"\"{p[1]}\"", type = "String")

    def p_literal_num(p):
        """ Literal : TkNum """
        p[0] = Literal(None, value=str(p[1]), type="int")

    def p_literal_bool(p):
        """
        Literal : TkTrue
                | TkFalse
        """
        p[0] = Literal(None, value=str(p[1]), type = "bool")

    def p_error(p):
        if p:
            column = p.lexpos - p.lexer.lexdata.rfind('\n', 0, p.lexpos)
            print(f"Sintax error in row {p.lineno}, column {column}: unexpected token '{p.value}'")
        else:
            print("Syntax error at EOF")
        sys.exit(1)

    parser = Yacc.yacc()
    result_ast = parser.parse(input_data, lexer=lexer)

    if result_ast:
        if errores:
            print(errores[0])
            sys.exit(1)
            
        combinators = """
Z = lambda g:(lambda x:g(lambda v:x(x)(v)))(lambda x:g(lambda v:x(x)(v)))
true = lambda x:lambda y:x
false = lambda x:lambda y:y
nil = lambda x:true
cons = lambda x:lambda y:lambda f: f(x)(y)
head = lambda p: p(true)
tail = lambda p:p(false)
apply = Z(lambda g:lambda f:lambda x:f if x==nil else g(f(head(x)))(tail(x)))
lift_do = lambda exp: lambda f: lambda g: lambda x: g(f(x)) if exp(x) else x
do = lambda exp: lambda f: Z(lift_do(exp)(f))
"""
        
        translator = LambdaTranslator()
        # La llamada a translate_block ahora devuelve la lambda final del programa
        program_lambda = translator.translate_block(result_ast)
        
        default_cons_list = "nil"
        for val in reversed(translator.main_block_defaults):
            default_cons_list = f"cons({val})({default_cons_list})"
        
        # La llamada al programa ahora es directa
        result_call = f"result = program({default_cons_list})"
        
        main_vars = translator.main_block_vars
        if main_vars:
            # FIX: El orden de los parámetros lambda se invierte para que coincida con la salida deseada.
            print_lambda_header = "lambda " + ":lambda ".join(reversed(main_vars)) + ":"
            print_dict = "{" + ", ".join([f"'{v}':{v}" for v in main_vars]) + "}"
            print_statement = f"print(apply({print_lambda_header}{print_dict})(result))"
        else:
            print_statement = "print('No variables declared in main block')"

        final_code = (
            f"{combinators}\n"
            f"program = {program_lambda}\n\n"
            f"{result_call}\n\n"
            f"{print_statement}\n"
        )
        
        output_filename = sys.argv[1].replace('.imperat', '.py')
        with open(output_filename, "w") as f:
            f.write(final_code)
        print(f"Traducción completada. Archivo generado: {output_filename}")

if __name__ == "__main__":
    main()