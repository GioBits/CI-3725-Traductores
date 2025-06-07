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

    def p_block(p):
        """
        Block : TkOBlock Declare Secuencing TkCBlock
        """

    def p_secuencing(p):
        """
        Secuencing : Declare TkSemicolon Declare
                   | Declare TkSemicolon Instruction
                   | Instruction TkSemicolon Instruction
        """
    def p_declare(p):
        """
        Declare : TkBool variable
                | TkInt variable
                | TkFunction range variable
                | empty
        range : TkOBracket TkSoForth TkNum TkCBracket
        variable : TkId Comma variable
                 | TkId
        Comma : TkComma
        """

    def p_instruction(p):
        """
        Instruction : Asig
                    | While
                    | If
                    | Print
                    | Skip
                    | empty
        """

    def p_asig(p):
        """
        Asig : Ident TkAsig expression
             | Ident TkAsig WriteFunction
        """
    def p_writefunction(p):
        """
        WriteFunction : TkFunction TkOpenPar expression TwoPoints expression TkClosePar WriteFunction
                     | empty
        TwoPoints : TkTowPoints
        """
    def p_app(p):
        """
        App : expression TkApp expression
        """
    def p_modificadores_flujo(p):
        """
        If : TkIf expression Then Instruction Guard TkFi
        Guard : TkGuard expression Then Instruction Guard
              | empty
        While : TkWhile expression Then Instruction TkEnd
        Then : TkArrow
        """

    def p_skip(p):
        """
        Skip : TkSkip
        """
    def p_print(p):
        """
        Print : TkPrint expression
        """

    # estudiar la forma como se expresa esta gramática
    def p_binary_expressions(p):
        """
        expression : expression Plus expression
                   | expression Minus expression
                   | expression Mult expression
                   | expression Equal expression 
                   | expression NEqual expression
                   | expression Leq expression
                   | expression Less expression
                   | expression Geq expression
                   | expression Greater expression
                   | expression And expression
                   | expression Or expression
                   | TkOpenPar expression TkClosePar
                   | Literal
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
        """
        if p[2] == "+":
            p[0] = p[1] + p[3]
        else:
            p[0] = p[1] - p[3]

    def p_unary_expression(p):
        """
        expression : Not expression %prec UMinus
                   | Minus expression
        Not : TkNot
        """

    # manejo de errores sintaticos

    def p_error(p):
        print("Sintax error")


    # constructor del parser

    parser = Yacc.yacc()







    # correr parser

    parser(input_data)
    





if __name__ == "__main__":
    main()
