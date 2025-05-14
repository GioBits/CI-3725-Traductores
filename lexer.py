# Owner(s):
# Date:
# Description:

import ply.yacc as Yacc
import ply.lex as Lex


def main():

    tokens = {
        "if" : "TkIf" ,
        "end" : "TkEnd" ,
        "while" : "TkWhile",
        "{" : "TkOBlock" ,
        "}" : "TkCBlock" ,
        ". ." : "TkSoForth" ,
        "," : "TkComma" ,
        "(" : "TkOpenPar" ,
        ")" : "TkClosePar" ,
        ":=" : "TkAsig" ,
        ";" : "TkSemicolon" ,
        "-->" : "TkArrow" ,
        "[]" : "TkGuard" ,
        "+" : "TkPlus" ,
        "-" : "TkMinus" ,
        "*" : "TkMult" ,
        "or" : "TkOr" ,
        "and" : "TkAnd" ,
        "!" : "TkNot" ,
        "<" : "TkLess" ,
        "<=" : "TkLeq" ,
        ">=" : "TkGeq" ,
        ">" : "TkGreater" ,
        "==" : "TkEqual" ,
        "<>" : "TkNEqual" ,
        "[" : "TkOBracket" ,
        "]" : "TkCBracket" ,
        ":" : "TkTowPoints" ,
        "." : "TkApp"   
        }





main()
