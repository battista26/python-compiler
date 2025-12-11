# Proje 3 Bütün Compiler Tasarımı
Python'da PLY (Python Lex-Yacc) kullanılarak tümüyle çalışan compiler projesi.  

Lexical Analysis -> Syntax Analysis(AST) -> Semantic Analysis (Type Checking & Scoping) -> Bytecode Generation -> Stack-Tabanlı Virtual Machine ile execution

## Gereksinimler
**Python 3.x**  
**PLY kütüphanesi**  
```bash
pip install ply
```

## Nasıl Çalıştırılır
Kendiniz yazarak test etmek istiyorsanız.  
```
python main.py
```
1. Bu komut çalıştırıldığında `code3` değerinin içindeki source kodu parse eder.  
2. AST yapısı oluşturulur.
3. Semantic analiz yapılır.
4. Bytecode oluşturulur
5. `program.bytecode` dosyasına bytecode kaydedilir.
6. Bytecode Virtual Machine'de çalıştırılır.  
(`program.bytecode` üzerinden okunma yapılmıyor, sadece test amaçlı oluşturulmakta)

---

Başka bir yöntem ise test case'leri çalıştırmak
```
python test_cases.py
```
## Programlama Dilinin Syntax'i
Veri tipleri:  
  - `int` Integer sayılar (ör: `5`, `-10`)  
  - `float` Float sayılar (ör: `3.14`)
  - `bool` Bool değerleri (ör: `true`, `false`)
  - `string` String literal (ör: `"Hello World"`)  

Syntax örnekleri:  

Artık değer bildiriminde veri tipi yazılması gerekiyor. `let` ile yazmayı kaldırdım. Bunun nedeni ise fonksiyon parametrelerinde veri tiplerinin belirtilmemesi karışıklığa sebep oluyor.  

```
int x = 11;
float armistice = 11.11;
string msg = "Nipah";
bool isActive = true;
```

Fonksiyonlar:  

return tipi ve parametreleri belirtilmek zorunda.
```
int topla(int a, int b) {
  return a + b;
}
```

Control Flow:
```
if (x > 5) {
    x = x - 1;
} else {
    x = x + 1;
}

while (num > 0) {
    num = num - 1;
}

for (i = 0; i < 10; i = i + 1) {
    # Loop body
}
```
# 4.yerde kaldım (Deepseek)


Yorumlar: Satır `#` ile başlarsa yorum yazılabilir

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