# Owner(s): Sergio Carrillo 14-11315 y David Pereira 18-10245
# Date: 19-05-2025
# Description: Proyecto Etapa1 CI-3725 Traductores e Interpretadores 

import ply.yacc as Yacc
import ply.lex as Lex
import sys


def main():
    """El algoritmo recibe como algoritmo de línea de comando el archivo.
        Hace un análisis de caracteres del archivo, reconoce los tokens
        del lenguaje e indica medinate errores por terminal cuando un 
        caracter que no pertenece a la gramática es introducido.
    """
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



    # entrada de la data

    lexer.input(input_data)

    # Lista para almacenar tokens
    tokens_found = []
    
    # procesamiento del dato
    for tok in lexer:
        column = find_column(input_data, tok)
        if (tok.type == "TkNum"):
            tokens_found.append(f"{tok.type}({tok.value}) {tok.lineno} {column}")
        elif (tok.type == "TkId"):
            tokens_found.append(f"{tok.type}(\"{tok.value}\") {tok.lineno} {column}")
        elif (tok.type == "TkString"):
            tokens_found.append(f"{tok.type}(\"{tok.value}\") {tok.lineno} {column}")
        else:
            tokens_found.append(f"{tok.type} {tok.lineno} {column}")

    # Si hay errores, solo mostrar los errores
    if errors:
        for error in errors:
            print(error)
    else:
        # Si no hay errores, mostrar los tokens
        for token in tokens_found:
            print(token)



if __name__ == "__main__":
    main()
