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
        "TkTwoPoints" ,
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
    t_TkTwoPoints = r"\:"
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
        def __init__(self,op = None, leftson = None, rightson = None):
            self.op = op
            self.leftson = leftson
            self.rightson = rightson


    class DeclareSection(Block): pass
    class Sequencing(Block):pass
    class SequencingDeclare(Block): pass
    class Declare(Block): pass
    class WriteFunction(Block): pass
    class Asig(Block): pass
    class If(Block): pass
    class While(Block): pass
    class Literal(Block): pass
    class Expr(Block): pass
    class Binary_expressions(Block):pass
    class Literal(Block):pass
    class Ident(Block): pass
    class String(Block):pass
    class UExpresson(Block): pass
    class Print(Block): pass
    class Skip(Block): pass
    class Guard(Block): pass
    class Then(Block): pass
    class TwoPoints(Block): pass


    # Se define la presedencia de los operadores
    # Desde menor presedencia a mayor y agrupación a izquierda

    precedence = (
        ("left", "TkOr"),
        ("left", "TkAnd"),
        ("left", "TkNEqual", "TkEqual", "TkLeq", "TkLess", "TkGreater", "TkGeq"),
        ("left", "TkPlus", "TkMinus"),
        ("left", "TkMult"),
        ("left", "TkApp"),
        ("right", "UMinus", "TkNot")  # menos unario
    )

    # Se define símbolo inicial
    start = "Block"
    # Se definen las reglas de la gramatica
    
    # permite recurción
    def p_Block(p):
        """
        Block : TkOBlock DeclareSection Sequencing TkCBlock
        """
        p[0] = Block("Block", p[2], p[3])

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
        p[0] = DeclareSection("Declare", p[1])


    def p_sequencing_declare_recursivo(p):
        """
        SequencingDeclare : SequencingDeclare Declare TkSemicolon
        """
        p[0] = SequencingDeclare("Sequencing", p[1], p[2])


    def p_sequencing_declare(p):
        """
        SequencingDeclare : Declare TkSemicolon
        """
        p[0] = p[1]

    def p_declare_int_bool(p):
        """
        Declare : TkBool TkId
                | TkInt TkId
        """
        p[0] = Declare(p[2] + " : " + p[1])



    def p_declare_function(p):
        """
        Declare : TkFunction TkOBracket TkSoForth Literal TkCBracket TkId
        """
        p[0] = Declare(p[6] + " : " + "function[.." + p[4].op + "]")

    # permite recursión
    def p_declare_int_bool_with_comma(p):
        """
        Declare : TkBool TkId Comma
                | TkInt TkId Comma
        """
        p[0] = Declare(p[2] + p[3] + " : " + p[1])
    # permite recursión
    def p_declare_function_with_comma(p):
        """
        Declare : TkFunction TkOBracket TkSoForth Literal TkCBracket TkId Comma
        """
        p[0] = Declare(p[6] + p[7] + " : " + "function[.." + p[4].op + "]")
    def p_comma(p):
        """
        Comma : TkComma TkId
        """
        p[0] = p[1] + " " + p[2]
    # permite recursión
    def p_comma_with_comma(p):
        """
        Comma : TkComma TkId Comma
        """
        p[0] = p[1] + " " + p[2] +  p[3]
    def p_asig(p):
        """
        Asig : Ident TkAsig expression
        """
        p[0] = Asig("Asig", p[1], p[3])


    #REvisarrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr



    def p_if(p):
        """
        If : TkIf Guard TkFi
        """
        p[0] = If("If", p[2])

    
    def p_guard0(p):
        """
        Guard : Guard TkGuard Then
        """
        p[0] = Guard("Guard", p[1], p[3])


    def p_guard1(p):
        """
        Guard : Then
        """
        p[0] = p[1]

    def p_while(p):
        """
        While : TkWhile Then TkEnd
        """
        p[0] = While("While", p[2])


    def p_then(p):
        """
        Then : expression TkArrow Sequencing
        """
        p[0] = Then("Then",p[1], p[3])


    #----------------------------------------------
    
    def p_skip(p):
        """
        Skip : TkSkip
        """
        p[0] = Skip("Skip")
        #p[0] = p[1]

    

    def p_print(p):
        """
        Print : TkPrint expression
        """
        p[0] = Print("Print", p[2])

    # estudiar la forma como se expresa esta gramática
    def p_binary_expressions(p):
        """
        expression : expression TkOr termino0
        termino0 : termino0 TkAnd termino1
        termino1 : termino1 TkEqual termino2
                 | termino1 TkNEqual termino2
                 | termino1 TkLeq termino2
                 | termino1 TkLess termino2
                 | termino1 TkGeq termino2
                 | termino1 TkGreater termino2
        termino2 : termino2 TkPlus termino3
                 | termino2 TkMinus termino3 
        termino3 : termino3 TkMult termino4
        termino4 : termino4 TkApp factor

        """
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

    
    def p_unary_expression(p):
        """
        factor : TkNot factor
                | TkMinus factor %prec UMinus
        """
        if p[1] == "!":
            p[0] = UExpresson("Not", p[2])
        elif p[1] =="-":
            p[0] = UExpresson("Minus", p[2])
    def p_factor(p):
        """
        factor : TkOpenPar expression TkClosePar
        """
        p[0] = p[2]

    def p_subtitutions(p):
        """
        expression : termino0
        termino0 : termino1
        termino1 : termino2
        termino2 : termino3
        termino3 : termino4
        termino4 : factor
        factor : Literal
               | Ident
               | String
        TwoPoints : TkTwoPoints
        """
        p[0] = p[1]

    

    
    
    def p_ident(p):
        """
        Ident : TkId
        """
        p[0] = Ident("Ident: " + p[1])
    def p_string(p):
        """
        String : TkString
        """
        p[0] = String("String: "+p[1])

    # manejo de errores sintaticos
    
    def p_literal(p):
        """
        Literal : TkNum
                | TkTrue
                | TkFalse
        """
        p[0] = Literal("Literal: " + str(p[1]))

    def p_error(p):
        if p:
            column = p.lexpos - p.lexer.lexdata.rfind('\n', 0, p.lexpos)
            if column <= 0: # Ajustar para casos donde el token está al inicio de línea
                column = p.lexpos + 1
            print(f"Sintax error in row {p.lineno}, column {column}: unexpected token '{p.value}'")
        else:
            print("Syntax error at EOF")
        sys.exit(1)



    # constructor del parser
    parser = Yacc.yacc()

    prueba = """
                {
                    int a;
                    if a -->
                        print "lee"
                    fi
                }
                """
    result = parser.parse(input_data)

    imprimir_ast(result,0)
    
    

def imprimir_ast( arbol , n):

    current = arbol
    nivel = n

    if current != None:
        print("-"*nivel+f"{current.op}")
        
        imprimir_ast( current.leftson, nivel+1)
        
        imprimir_ast( current.rightson, nivel+1)


if __name__ == "__main__":
    main()
