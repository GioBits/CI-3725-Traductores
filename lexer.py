# Owner(s):
# Date:
# Description:

import ply.yacc as Yacc
import ply.lex as Lex


def main():

    tokens = (
        "TkIf" ,
        "TkEnd" ,
        "TkWhile" ,
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
        "TkOr" ,
        "TkAnd" ,
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
        "TkApp" ,
        "TkNum",
        "TkTrue", #########
        "TkFalse",#########
        "TkSkip",
        "TkString",     # De aquí para abajo me falta agregar reglas
        "TkId"

    )

    # tokens sencillos

    t_TkIf = "if"
    t_TkEnd = "end"
    t_TkWhile = "while"
    t_TkOBlock = r"\{"
    t_TkCBlock = r"\}"
    t_TkSoForth = r"\. \."   #revisar esto bien
    t_TkComma = r"\,"       #no se si sea necesario de esta forma
    t_TkOpenPar = r"\("
    t_TkClosePar = r"\)"
    t_TkAsig = r"\:\="
    t_TkSemicolon = r"\;"
    t_TkArrow = r"\-\-\>"
    t_TkGuard = r"\[\]"
    t_TkPlus = r"\+"
    t_TkMinus = r"\-"
    t_TkMult = r"\*"
    t_TkOr = "or"
    t_TkAnd = "and"
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
    t_TkTrue = "true"
    t_TkFalse = "false"
    t_TkSkip = "skip"

    # tokens especiales

    def t_TkNum( t ):
        r"\d+"
        t.value = int(t.value)
        return t

    # tokens ignorados

    t_ignore = " \t\n" # revisar que esto no genere problemas

    # conteo de lineas 
    
    def t_newline( t ):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # manejo de errores 
    
    def t_error( t ):
        print( f"Error: Unexpected character \"{t.value[0]}\" in row {t.lineno}, column {t.lexpos}")
        t.lexer.skip(1)


    # llamada al contructor lexico

    lexer = Lex.lex()



    # dato de prueba

    prueba = """
    3 + 4 * 10 ( and while )
    + -20 *2  :,=@=    
    """

    # entrada del dato

    lexer.input( prueba )

    # procesamiento del dato
    # se itera sobre lo que parece una secuencia del tipo LexToken
    for tok in lexer:
        # hay ciertos atributos en Lextoken entre ellos
        # el tipo que los definimos nostros, el valor 
        # la línea y la posición según lo que pidió flaviani

        if ( tok.type == "TkNum" ):
            print( f"{tok.type}({tok.value}) {tok.lineno} {tok.lexpos}")
        else:
            print( f"{tok.type} {tok.lineno} {tok.lexpos}")



main()
