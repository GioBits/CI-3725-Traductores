# Owner(s): Sergio Carrillo 14-11315 y David Pereira 18-10245
# Date: 15 de junio de 2025 (Actualizado)
# Description: Analizador léxico (lexer) para el lenguaje imperativo,
#              utilizando PLY. Contiene la definición de tokens y reglas léxicas.

import ply.lex as Lex    # Importa el módulo Lex de PLY para el analizador léxico

# Palabras reservadas del lenguaje.
# Un diccionario que mapea las palabras clave (strings) a sus nombres de token.
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

# Lista de todos los nombres de tokens reconocidos por el lexer.
# Incluye tokens para operadores, delimitadores, tipos de datos, identificadores,
# literales y las palabras reservadas.
tokens = [
    "TkOBlock" ,    # {
    "TkCBlock" ,    # }
    "TkSoForth" ,   # .. (operador "hasta" para funciones)
    "TkComma" ,     # ,
    "TkOpenPar" ,   # (
    "TkClosePar" ,  # )
    "TkAsig" ,      # := (operador de asignación)
    "TkSemicolon" , # ;
    "TkArrow" ,     # --> (separador en guardias y bucles while)
    "TkGuard" ,     # [] (operador de guardia anidada)
    "TkPlus" ,      # +
    "TkMinus" ,     # -
    "TkMult" ,      # *
    "TkNot" ,       # ! (negación lógica)
    "TkLess" ,      # <
    "TkLeq" ,       # <=
    "TkGeq" ,       # >=
    "TkGreater" ,   # >
    "TkEqual" ,     # ==
    "TkNEqual" ,    # <> (no igual)
    "TkOBracket" ,  # [
    "TkCBracket" ,  # ]
    "TkTwoPoints" , # : (dos puntos para acceso a funciones)
    "TkApp",        # . (operador de aplicación o acceso a miembros)
    "TkNum",        # Números enteros
    "TkString",     # Cadenas de texto
    "TkId"          # Identificadores (nombres de variables, funciones)
] + list(reserved.values()) # Añade los valores de las palabras reservadas a la lista de tokens

# Definiciones de expresiones regulares para tokens simples.
# Cada 't_' prefijo indica una regla de token. PLY usa estas para el reconocimiento léxico.
t_TkOBlock = r"\{"
t_TkCBlock = r"\}"
t_TkSoForth = r"\. \."   # Expresión regular para '..'
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

# Tokens con reglas de expresiones regulares más complejas o lógica adicional.
# Estas funciones permiten realizar acciones cuando se reconoce un token.

def t_COMMENT(t):
    r'//.*'
    # Ignora las líneas que comienzan con '//' (comentarios de una sola línea).
    pass  # No retorna valor, por lo tanto, el lexer ignora este token.
    
def t_TkId(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    # Reconoce identificadores que comienzan con una letra o guion bajo, seguidos de letras, números o guiones bajos.
    # Verifica si el identificador es una palabra reservada. Si lo es, su tipo de token cambia al de la palabra reservada.
    t.type = reserved.get(t.value, "TkId")
    return t

def t_TkString(t):
    r'"[^"\\\n]*(?:\\[n"\\][^"\\\n]*)*"'
    # Reconoce cadenas de texto encerradas entre comillas dobles, permitiendo caracteres escapados como \n, \", \\.
    t.value = t.value[1:-1]  # Elimina las comillas del principio y final del valor del token.
    return t

def t_TkNum(t):
    r"\d+"
    # Reconoce secuencias de uno o más dígitos como números enteros.
    t.value = int(t.value)   # Convierte la cadena de dígitos a un valor entero.
    return t

# Lista global para almacenar los errores léxicos encontrados.
errors = []  

def t_error(t):
    # Función que se llama cuando el lexer encuentra un carácter inesperado.
    # Calcula la columna del error para un mensaje más informativo.
    column = t.lexpos - t.lexer.lexdata.rfind('\n', 0, t.lexpos)
    if column <= 0: # Ajustar para casos donde el token está al inicio de la línea
        column = t.lexpos + 1
    errors.append(f"Error: Carácter inesperado \"{t.value[0]}\" en fila {t.lineno}, columna {column}")
    t.lexer.skip(1) # Avanza el lexer un carácter para intentar recuperarse.

# Tokens ignorados por el lexer (espacios en blanco y tabulaciones).
t_ignore = " \t"

# Conteo de líneas.
# Actualiza el número de línea del lexer cada vez que encuentra uno o más saltos de línea.
def t_newline( t ):
    r"\n+"
    t.lexer.lineno += len(t.value)

def get_lexer_and_tokens(input_data):
    """
    Función para construir y obtener el objeto lexer de PLY y la lista de tokens.

    Args:
        input_data (str): La cadena de texto del programa fuente a analizar.

    Returns:
        tuple: Una tupla que contiene:
            - lexer (ply.lex.Lexer): El objeto lexer configurado.
            - tokens (list): La lista de nombres de tokens reconocidos.
            - errors (list): La lista de errores léxicos encontrados durante el análisis inicial.
    """
    # Reinicia la lista de errores para cada nueva llamada.
    global errors
    errors = [] 

    # Construir el analizador léxico (lexer).
    _lexer = Lex.lex()
    _lexer.input(input_data) # Alimentar el lexer con los datos de entrada para generar los tokens.
    
    return _lexer, tokens, errors

