import ply.yacc as yacc
from ast_function import print_ast
from lexer import tokens, lexer
from ast_structure import (
    Program, Blok, DegiskenBildir, FonksiyonBildir, Atama,
    IfStatement, WhileStatement, ForStatement, ReturnStatement,
    BinaryOp, UnaryOp, FonksiyonCall, Literal, Tanimlayici
)

# Oncelik Kurallari
# Operasyon onceligi, 10 + 20 * 30 seklinde ifadelerde dogru AST olusturmak icin
precedence = (
    ('left', 'VEYA'),
    ('left', 'VE'),
    ('left', 'ESIT', 'ESIT_DEGIL'),
    ('left', 'KUCUK', 'KUCUK_ESIT', 'BUYUK', 'BUYUK_ESIT'),
    ('left', 'TOPLA', 'CIKAR'),
    ('left', 'CARP', 'BOL', 'MODUL'),
    ('right', 'DEGIL'),  # Unary NOT (!)
    ('right', 'UMINUS'), # Unary Eksi (-5)
)

# Gramer Kurallari

def p_program(p):
    '''program : statement_list
               | empty'''
    p[0] = Program(p[1])

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : var_decl
                 | func_decl
                 | assignment_stmt
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | return_stmt
                 | expr_stmt
                 | blok'''
    p[0] = p[1]

# Bloklar
def p_blok(p):
    '''blok : SOL_SUSLU_PARANTEZ statement_list SAG_SUSLU_PARANTEZ
            | SOL_SUSLU_PARANTEZ SAG_SUSLU_PARANTEZ'''
    if len(p) == 4:
        p[0] = Blok(p[2])
    else:
        p[0] = Blok([])


# Farklı tipler
def p_tip(p):
    '''tip : TIP_INT
           | TIP_FLOAT
           | TIP_BOOL
           | TIP_VOID
           | TIP_STRING'''
    p[0] = p[1]  # 'int', 'float', 'bool', 'void', 'string' string degerleri

# Bildirmeler

# let x = 10; seklinde veya
# let x; seklinde yazabiliriz. Ikinci durumda 'None' degeri atanir.
# Artik int x = 10; seklinde tip belirterek de bildirebiliyoruz.
def p_var_decl(p):
    '''var_decl : tip TANIMLAYICI ATAMA expression NOKTALI_VIRGUL
                | tip TANIMLAYICI NOKTALI_VIRGUL'''
    if len(p) == 6:
        p[0] = DegiskenBildir(isim=p[2], tip=p[1], deger=p[4])
    else:
        p[0] = DegiskenBildir(isim=p[2], tip=p[1], deger=None)

def p_func_decl(p):
    '''func_decl : tip TANIMLAYICI SOL_PARANTEZ param_list SAG_PARANTEZ blok
                 | TIP_VOID TANIMLAYICI SOL_PARANTEZ param_list SAG_PARANTEZ blok'''
    p[0] = FonksiyonBildir(isim=p[2], return_type=p[1], parametreler=p[4], govde=p[6])

def p_param_list(p):
    '''param_list : param_list VIRGUL param
                  | param
                  | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_param(p):
    '''param : tip TANIMLAYICI'''
    p[0] = (p[1], p[2])

# if, while, for, return statementlari

def p_if_stmt(p):
    '''if_stmt : IF SOL_PARANTEZ expression SAG_PARANTEZ blok
               | IF SOL_PARANTEZ expression SAG_PARANTEZ blok ELSE blok'''
    if len(p) == 6:
        p[0] = IfStatement(condition=p[3], true_blok=p[5])
    else:
        p[0] = IfStatement(condition=p[3], true_blok=p[5], else_blok=p[7])

def p_while_stmt(p):
    '''while_stmt : WHILE SOL_PARANTEZ expression SAG_PARANTEZ blok'''
    p[0] = WhileStatement(condition=p[3], govde=p[5])

# for loop'ta hem for(let i = 0; ...) hem de for(i = 0) şeklinde yazabilmeyi eklemek için ayrı kural ekledim
def p_for_init(p):
    '''for_init : var_decl
                | assignment_stmt'''
    p[0] = p[1]

def p_for_stmt(p):
    '''for_stmt : FOR SOL_PARANTEZ for_init expression NOKTALI_VIRGUL assignment SAG_PARANTEZ blok'''
    # Format: for (let i=0; i<10; i=i+1) { ... }
    # for_init'in sonunda NOKTALI_VIRGUL var o yuzden yazmamiza gerek yok
    p[0] = ForStatement(init=p[3], condition=p[4], update=p[6], govde=p[8])

def p_return_stmt(p):
    '''return_stmt : RETURN expression NOKTALI_VIRGUL'''
    p[0] = ReturnStatement(p[2])

# Assignment

def p_assignment_stmt(p):
    '''assignment_stmt : assignment NOKTALI_VIRGUL'''
    p[0] = p[1]

def p_assignment(p):
    '''assignment : TANIMLAYICI ATAMA expression'''
    p[0] = Atama(isim=p[1], deger=p[3])

def p_expr_stmt(p):
    '''expr_stmt : expression NOKTALI_VIRGUL'''
    p[0] = p[1] # Expression statement olabilir

# Expressions

def p_expression_binop(p):
    '''expression : expression TOPLA expression
                  | expression CIKAR expression
                  | expression CARP expression
                  | expression BOL expression
                  | expression MODUL expression
                  | expression ESIT expression
                  | expression ESIT_DEGIL expression
                  | expression KUCUK expression
                  | expression BUYUK expression
                  | expression KUCUK_ESIT expression
                  | expression BUYUK_ESIT expression
                  | expression VE expression
                  | expression VEYA expression'''
    p[0] = BinaryOp(sol=p[1], op=p[2], sag=p[3])

# Negatif sayilar öncelikli oldugundan %prec ile precedence override diyoruz
def p_expression_unary(p):
    '''expression : CIKAR expression %prec UMINUS
                  | DEGIL expression'''
    p[0] = UnaryOp(op=p[1], expr=p[2])

def p_expression_group(p):
    '''expression : SOL_PARANTEZ expression SAG_PARANTEZ'''
    p[0] = p[2]

def p_expression_call(p):
    '''expression : TANIMLAYICI SOL_PARANTEZ arg_list SAG_PARANTEZ'''
    p[0] = FonksiyonCall(isim=p[1], args=p[3])

def p_arg_list(p):
    '''arg_list : arg_list VIRGUL expression
                | expression
                | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_expression_literal(p):
    '''expression : TAMSAYI
                  | ONDALIKLI
                  | DOGRU
                  | YANLIS
                  | STRING'''
    
    # p.slice[1] is the token object for the first symbol on the right side
    token_type = p.slice[1].type 
    
    if token_type == 'DOGRU':
        val, type_ = True, 'bool'
    elif token_type == 'YANLIS':
        val, type_ = False, 'bool'
    elif token_type == 'STRING':
        val, type_ = p[1], 'string'
    elif token_type == 'ONDALIKLI':
        val, type_ = p[1], 'float'
    else:
        # Default fallback is integer (TAMSAYI)
        val, type_ = p[1], 'int'
    
    p[0] = Literal(deger=val, tip=type_)

def p_expression_id(p):
    '''expression : TANIMLAYICI'''
    p[0] = Tanimlayici(isim=p[1])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        raise Exception(f"Syntax hatasi, token {p.type}, deger '{p.value}', satir {p.lineno}")
    else:
        raise Exception("Syntax hatasi, dosya sonu EOF")

# Build parser
parser = yacc.yacc()

# Test Helper

# 3 * 4 + 5 yazdığımızda (3 * 4) + 5 mü 3 * (4 + 5) mi verecek?

test_code = """
int x = 10;
int y = 20;
def topla(int a, int b) {
    return a + b;
}
"""

if __name__ == "__main__":
    #test_code = input("Test kodunu girin:\n")

    print("--- Parsing Code ---")
    print(test_code)
    print("--- AST Result ---")
    result = parser.parse(test_code)
    print_ast(result)