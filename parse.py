# Owner(s): Sergio Carrillo 14-11315 y David Pereira 18-10245
# Date: 
# Description: Proyecto Etapa2 CI-3725 Traductores e Interpretadores 

import ply.yacc as Yacc
import ply.lex as Lex
import sys


def main():
    # Verificar que se proporcionó un archivo como argumento
    if len(sys.argv) != 2:
        print("Error: Por favor proporcione un archivo .imperat como argumento")
        print("Uso: python lexer.py archivo.imperat")
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

    # palabras reservadas del lenguaje
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
        "TkTowPoints" ,
        "TkApp",
        "TkNum",
        "TkString",
        "TkId"

    ] + list(reserved.values())



    # tokens sencillos

    t_TkOBlock = r"\{"
    t_TkCBlock = r"\}"
    t_TkSoForth = r"\. \."   
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
    t_TkTowPoints = r"\:"
    t_TkApp = r"\."

    # tokens especiales

    def t_COMMENT(t):
        r'//.*'
        pass  # No retorna nada - ignora los comentarios
        
    def t_TkId(t):
        r"[a-zA-Z_][a-zA-Z_0-9]*"
        t.type = reserved.get(t.value, "TkId")
        return t

    def t_TkString(t):
        r'"[^"\\\n]*(?:\\[n"\\][^"\\\n]*)*"'
        t.value = t.value[1:-1]  # Remover las comillas
        return t

    def t_TkNum(t):
        r"\d+"
        t.value = int(t.value)
        return t

    # manejo de errores 
    errors = []  # Lista para almacenar errores

    def t_error(t):
        column = t.lexpos - t.lexer.lexdata.rfind('\n', 0, t.lexpos)
        if column <= 0:
            column = t.lexpos + 1
        errors.append(f"Error: Unexpected character \"{t.value[0]}\" in row {t.lineno}, column {column}")
        t.lexer.skip(1)

    # Actualizar la posición de la columna
    def find_column(input, token):
        last_cr = input.rfind('\n', 0, token.lexpos)
        if last_cr < 0:
            last_cr = -1
        column = (token.lexpos - last_cr)
        return column

    # tokens ignorados

    t_ignore = " \t"

    # conteo de lineas 
    
    def t_newline( t ):
        r"\n+"
        t.lexer.lineno += len(t.value)


    # llamada al contructor lexico

    lexer = Lex.lex()

    # entrada de la data para los tokens

    lexer.input(input_data)

    #------------------------------------------------
    # Etapa2
    #------------------------------------------------



    class Block():
        def __init__(self,type = None, lefson = None, rightson = None, op = None):
            self.type = type
            self.lefson = lefson
            self.rightson = rightson
            self.op = op

    class Declare(Block): pass
    class Secuencing(Block):pass
    class Asig(Block): pass
    class If(Block): pass
    class Gruar(Block): pass
    class While(Block): pass
    class Literal(Block): pass
    class Expr(Block): pass


    class Binary_expressions(Expr):pass

    # Se define la presedencia de los operadores
    # Desde menor presedencia a mayor y agrupación a izquierda

    precedence = (
        ("left", "TkAnd", "TkOr"),
        ("left", "TkNEqual", "TkEqual", "TkLeq", "TkLess", "TkGreater", "TkGeq"),
        ("left", "TkPlus", "TkMinus"),
        ("left", "TkMult"),
        ("right", "UMinus", "TkNot")  # menos unario
    )

    # Se define símbolo inicial
    start = "Block"
    # Se definen las reglas de la gramatica
    
    def p_empty(p):
        "empty :"
        pass


    def p_Block(p):
        """
        Block : TkOBlock Secuencing TkCBlock
        """
        p[0] = ["Block", p[2]]
    # permite recurción
    def p_Block_DeclareSection(p):
        """
        Block : TkOBlock DeclareSection Secuencing TkCBlock
        """
        p[0] = ["Block", p[2], p[3]]

    def p_Block_DeclareSection_only(p):
        """
        Block : TkOBlock DeclareSection TkCBlock
        """
        p[0] = ["Block", p[2]]

    def p_secuencing(p):
        """
        Secuencing : Secuencing TkSemicolon Instruction
        """
        p[0] = ["Secuencing", p[1], p[3]]

    def p_secuencing(p):
        """
        Secuencing : Instruction
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
        DeclareSection : SecuencingDeclare
        """
        p[0] = ["Declare", p[1]]

    def p_secuencing_declare_recursivo(p):
        """
        SecuencingDeclare : Declare TkSemicolon SecuencingDeclare
        """
        p[0] = ["Secuencing", p[1], p[3]]

    def p_secuencing_declare(p):
        """
        SecuencingDeclare : Declare TkSemicolon
        """
        p[0] = p[1]

    def p_declare_int_bool(p):
        """
        Declare : TkBool Ident
                | TkInt Ident
        """
        p[0] = [p[2], p[1]]


    def p_declare_function(p):
        """
        Declare : TkFunction TkOBracket TkSoForth Literal TkCBracket Ident
        """
        p[0] = ["WriteFunction", p[6], p[1], p[2], p[3], p[4], p[5]]
    # permite recursión
    def p_declare_int_bool_with_comma(p):
        """
        Declare : TkBool Ident Comma
                | TkInt Ident Comma
        """
        p[0] = [p[1], p[2]] + p[3]
    # permite recursión
    def p_declare_function_with_comma(p):
        """
        Declare : TkFunction TkOBracket TkSoForth Literal TkCBracket Ident Comma
        """
        p[0] = ["WriteFunction", p[6]] + p[7] + [p[1], p[2], p[3], p[4], p[5]] 
    def p_comma(p):
        """
        Comma : TkComma Ident
        """
        p[0] = [p[1], p[2]]
    # permite recursión
    def p_comma_with_comma(p):
        """
        Comma : TkComma Ident Comma
        """
        p[0] = [p[1], p[2], p[3]]
    def p_asig(p):
        """
        Asig : Ident TkAsig expression
             | Ident TkAsig WriteFunction
        """
        p[0] = [p[1], p[2], p[3]]
    def p_writefunction(p):
        """
        WriteFunction : Ident acceso
        """
        p[0] = [p[1], p[2]]
    def p_acceso_funcion(p):
        """
        acceso : TkOpenPar expression TwoPoints expression TkClosePar
        """
        p[0] = [p[1], p[2], p[3], p[4], p[5]]

    def p_acceso_funcion_recursivo(p):
        """
        acceso : TkOpenPar expression TwoPoints expression TkClosePar acceso
        """
        p[0] = [p[1], p[2], p[3], p[4], p[5], p[6]]

    def p_if(p):
        """
        If : TkIf expression Then Instruction Guard TkFi
        """
        p[0] = [p[1], p[2], p[3], p[4], p[5], p[6]]
    def p_while(p):
        """
        While : TkWhile expression Then Instruction TkEnd
        """
        p[0] = [p[1], p[2], p[3], p[4], p[5]]
    def p_guard(p):
        """
        Guard : TkGuard expression Then Instruction
        """
        p[0] = [p[1], p[2], p[3], p[4]]
    def p_guard_empty(p):
        """
        Guard : empty
        """
        p[0] = p[1]

    def p_skip(p):
        """
        Skip : TkSkip
        """
        p[0] = p[1]

    def p_print(p):
        """
        Print : TkPrint expression
        """
        p[0] = [p[0], p[2]]

    # estudiar la forma como se expresa esta gramática
    def p_binary_expressions(p):
        """
        expression : expression Plus termino
                   | expression Minus termino
                   | expression Equal termino 
                   | expression NEqual termino
                   | expression Leq termino
                   | expression Less termino
                   | expression Geq termino
                   | expression Greater termino
                   | expression And termino
                   | expression Or termino
                   | expression TkApp termino
        termino : termino Mult factor
        """
        p[0] = [p[2], p[1], p[3]]
        
    def p_unary_expression(p):
        """
        factor : Not factor
                | Minus factor %prec UMinus
        """
        p[0] = [p[1], p[2]]
    def p_factor(p):
        """
        factor : TkOpenPar expression TkClosePar
        """
        p[0] = [p[1], p[2], p[3]]



    def p_subtitutions(p):
        """
        expression : termino
        termino : factor
        factor : Literal
               | Ident
               | String
        And : TkAnd
        Or : TkOr
        Mult : TkMult
        NEqual : TkNEqual
        Equal : TkEqual
        Leq : TkLeq
        Less : TkLess
        Geq : TkGeq
        Greater : TkGreater
        Plus : TkPlus
        Minus : TkMinus
        Literal : TkNum
                | TkTrue
                | TkFalse
        Ident : TkId
        String : TkString
        TwoPoints : TkTowPoints
        Then : TkArrow
        Not : TkNot
        """
        p[0] = p[1]

    # manejo de errores sintaticos

    def p_error(p):
        print("Sintax error")


    # constructor del parser
    parser = Yacc.yacc()

    prueba = """
                {
                    int b;
                }
                """
    result = parser.parse(prueba)
    
    n = 0
    
    print(result)
    print("-"*n+f"{result[0]}")
    n += 1
    print("-"*n+f"{result[1][0]}")
    n += 1
    


    #print(current.rightson)
    #imprimir_ast(result, 0)
    


    
def imprimir_ast(arbol, n):

    current = arbol
    space = n
    operation = None

    if current != None:
        print("-"*space+f"{current.type}")
        rightson = current.rightson
        leftson = current.leftson
    
        imprimir_ast(rightson, n+1)
        imprimir_ast(leftson, n+1)






if __name__ == "__main__":
    main()
