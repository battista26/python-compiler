import ply.lex as lex

# 1. Update Reserved Words to include Types, Remove 'let'
reserved = {
    'def': 'DEF',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'return': 'RETURN',
    'true': 'DOGRU',
    'false': 'YANLIS',
    'string': 'TIP_STRING',
    'int': 'TIP_INT',
    'float': 'TIP_FLOAT',
    'bool': 'TIP_BOOL',
    'void': 'TIP_VOID'
}

# 2. Update Token List
tokens = [
    'TANIMLAYICI',
    'TAMSAYI',
    'ONDALIKLI',

    'TOPLA',
    'CIKAR',
    'CARP',
    'BOL',
    'MODUL',

    'ATAMA',
    'ESIT',
    'ESIT_DEGIL',
    'KUCUK',
    'BUYUK',
    'KUCUK_ESIT',
    'BUYUK_ESIT',

    'VE',
    'VEYA',
    'DEGIL',
    
    'SOL_PARANTEZ',
    'SAG_PARANTEZ',
    'SOL_SUSLU_PARANTEZ',
    'SAG_SUSLU_PARANTEZ',
    'SOL_KOSELI_PARANTEZ',
    'SAG_KOSELI_PARANTEZ',

    'NOKTALI_VIRGUL',
    'VIRGUL',

    'STRING'
] + list(reserved.values())

# Regex Rules
t_TOPLA = r'\+' 
t_CIKAR = r'-'
t_CARP = r'\*'
t_BOL = r'/'
t_MODUL = r'%'
t_ATAMA = r'='
t_ESIT = r'=='
t_ESIT_DEGIL = r'!='
t_KUCUK = r'<'
t_BUYUK = r'>'
t_KUCUK_ESIT = r'<='
t_BUYUK_ESIT = r'>='
t_VE = r'&&'
t_VEYA = r'\|\|'
t_DEGIL = r'!'
t_SOL_PARANTEZ = r'\('
t_SAG_PARANTEZ = r'\)'
t_SOL_SUSLU_PARANTEZ = r'\{'
t_SAG_SUSLU_PARANTEZ = r'\}'
t_SOL_KOSELI_PARANTEZ = r'\['
t_SAG_KOSELI_PARANTEZ = r'\]'
t_NOKTALI_VIRGUL = r';'
t_VIRGUL = r','

t_ignore = ' \t\r'

def t_YORUM(t):
    r'\#.*'
    pass 

def t_ONDALIKLI(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_TAMSAYI(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]  # Remove quotes
    t.type = 'STRING'
    return t

def t_TANIMLAYICI(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'TANIMLAYICI')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Geçersiz karakter '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()