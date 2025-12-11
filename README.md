# Proje 2 Python'da Parser ve AST Oluşurulması
Python'da PLY kullanılarak Lexer ve Parser projesi.
## Gereksinimler
Python 3.x  
PLY kütüphanesi
`pip install ply`

## Nasıl Çalıştırılır
Kendiniz yazarak test etmek istiyorsanız.  
```
python parser.py
```

---

Başka bir yöntem ise test case'leri çalıştırmak
```
python test_cases.py
```
## Programlama Dilinin Syntax'i
- Değişkenler (variables): `let` kelimesiyle bildirilebilir.  
  - `let x = 10;`
  - `let y = 25;`
  - `let x;`
- Fonksiyonlar: `def` kelimesiyle bildirilebilir.
  - `def fonksiyonum(a, b) { ... }`
  - `def topla(a, b) { return a + b }`
- Kontrol akışı (control flow):
  - `if (condition) { ... } else { ... }`
  - `while (condition) { ... }`
  - `for (let i=0; i<10; i=i+1) { ... }`
- Veri tipleri: Integer(`11`), Float(`11.11`), Boolean(`True`, `False`)
- Yorumlar: Satır `#` ile başlarsa yorum yazılabilir

## Gramer (EBNF)
```
program        ::= statement_list?
statement_list ::= statement | statement_list statement
statement      ::= var_decl | func_decl | assignment_stmt | if_stmt | while_stmt | for_stmt | return_stmt | expr_stmt | block

block          ::= "{" statement_list "}" | "{" "}"

var_decl       ::= "let" IDENTIFIER ("=" expression)? ";"
func_decl      ::= "def" IDENTIFIER "(" param_list? ")" block
param_list     ::= IDENTIFIER ("," IDENTIFIER)*

if_stmt        ::= "if" "(" expression ")" block ("else" block)?
while_stmt     ::= "while" "(" expression ")" block
for_stmt       ::= "for" "(" for_init expression ";" assignment ")" block
for_init       ::= var_decl | assignment_stmt

assignment_stmt::= assignment ";"
assignment     ::= IDENTIFIER "=" expression
return_stmt    ::= "return" expression ";"
expr_stmt      ::= expression ";"

expression     ::= expression BINOP expression
                 | UNARYOP expression
                 | "(" expression ")"
                 | IDENTIFIER "(" arg_list? ")"
                 | LITERAL
                 | IDENTIFIER

BINOP          ::= "+" | "-" | "*" | "/" | "%" | "==" | "!=" | "<" | ">" | "<=" | ">=" | "&&" | "||"
UNARYOP        ::= "-" | "!"
```
## AST Node Yapısı
`ast_structure.py` dosyasında sınıflandırılmalar bulunmakta.

- Program: Root node, statement'ların listesini içerir.

- Blok: `{}` gibi bloklari temsil eder.

- Declarationlar:

  - DegiskenBildir: Değişken adı ve verilen değer (None da olarabilir).

  - FonksiyonBildir: Fonksiyon adı, parametre listesi ve gövde bloğu bulundurur.

- Statementlar:

  - IfStatement: Condition, doğru bloğu ve opsiyonel else bloğu.

  - WhileStatement: Condition ve gövde bloğu.

  - ForStatement: Initialization, condition, update ve gövde.

  - ReturnStatement: Dönüş değeri döndürür.

  - Atama: Değişken ismi ve yeni değer.

- Expressionlar:

  - BinaryOp: Sol, operatör, sağ node'u.

  - UnaryOp: Operatör ve expression node'u.

  - FonksiyonCall: Fonksiyon adı ve argüman listesi.

  - Literal: Değer ve tür (int, float, bool).

  - Tanimlayici: Değişken adı araması.