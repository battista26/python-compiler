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
    # Döngü gövdesi
}
```
Yorumlar: `#` ile başlayan satırlarla yorum yazılabilir  

## İmplementasyon Detayları  
Code generation'dan önce Semantic Analysis için Visitor Pattern (`semantic_analyzer.py`) kullanılıyor.
- Symbol Table: (`symbol_table.py`) Scope'u stack olarak belirtir (Global -> Fonksiyon -> Blok)
- Scope Resolution: `{ ... }` şeklindeki bloklardan çıkıldığında değişkenler sembol tablosundan kaldırılır.
- Type Checking:
  - Değişkenler atanan değerlere uyuşmalı
  - Binary operasyonları (ör: `+`, `>`) uyumlu tipler arasında olmalı  
  - Fonksiyon argümanları belirtilen tipe şekle uymalı
  - Fonksiyon return değeri belirtilen tipte return tipi döndürür

## Kullanılan Mimari: Stack-Based Bytecode

MIPS/x86 spesifik hardware register'ları kullandığı için platform-independent Bytecode daha kolay.  

Ayrıca compiler Python'da yazıldığından VM ile test etmek daha basit.

## Bazı Eksiklerler
Array, Struct gibi eklenmedi.  
Input gibi diğer dillerde kütüphanede olan fonksiyonlar yok.

## Örnek Output
```
int x = 5 + 3;
```
Oluşan Bytecode (`program.bytecode`)
```
LOAD_CONST,5
LOAD_CONST,3
ADD
STORE_VAR,x
HALT
```
Virtual Machine Outputu
```
--- VM Calisiyor ---
 > x = 8
Program sonlandi.
--- VM Bitti ---
Final Memory State: {'x': 8}
```

Bütün Compiler Output (Tüm programın nasıl çalıştığını görmek için)  
```
python main.py
==========================================

--- Compiler Design Project ---

--- Source Code ---
int x = 5 + 3;


--- Lexical Analysis ---
Tipi: TIP_INT         Degeri: int
Tipi: TANIMLAYICI     Degeri: x
Tipi: ATAMA           Degeri: =
Tipi: TAMSAYI         Degeri: 5
Tipi: TOPLA           Degeri: +
Tipi: TAMSAYI         Degeri: 3
Tipi: NOKTALI_VIRGUL  Degeri: ;
------------------------------------


--- Syntax Analysis (Parsing) ---
AST Tree Olusturuldu:
Program
  statements: [
    DegiskenBildir
      isim: x
      tip: int
      deger:
        BinaryOp
          sol:
            Literal
              deger: 5
              tip: int
          op: +
          sag:
            Literal
              deger: 3
              tip: int
  ]

--- Semantic Analysis ---
Analiz Basliyor...
--- Global Scope (Derinlik: 0) ---
  x: {'type': 'int', 'category': 'var'}
------------------------------
Analiz Bitti.
----------------------------


--- Bytecode Generation ---
0  : LOAD_CONST      5
1  : LOAD_CONST      3
2  : ADD
3  : STORE_VAR       x
4  : HALT
------------------------------


[INFO] Bytecode'program.bytecode' dosyasina kaydedildi.

--- Virtual Machine Execution ---
--- VM Calisiyor ---
 > x = 8
Program sonlandi.
--- VM Bitti ---
Final Memory State: {'x': 8}
==========================================
```

## Gramer (EBNF)
```
/* High Level Structure */
program          ::= statement_list?
statement_list   ::= statement | statement_list statement
statement        ::= var_decl 
                   | func_decl 
                   | assignment_stmt 
                   | if_stmt 
                   | while_stmt 
                   | for_stmt 
                   | return_stmt 
                   | expr_stmt 
                   | blok

blok             ::= "{" statement_list "}" | "{" "}"

/* Data Types */
tip              ::= "int" | "float" | "bool" | "string" | "void"

/* Declarations */
var_decl         ::= tip TANIMLAYICI ("=" expression)? ";"
func_decl        ::= tip TANIMLAYICI "(" param_list? ")" blok
param_list       ::= param ("," param)*
param            ::= tip TANIMLAYICI

/* Control Flow */
if_stmt          ::= "if" "(" expression ")" blok ("else" blok)?
while_stmt       ::= "while" "(" expression ")" blok
for_stmt         ::= "for" "(" for_init expression ";" assignment ")" blok
for_init         ::= var_decl | assignment_stmt

/* Statements */
assignment_stmt  ::= assignment ";"
assignment       ::= TANIMLAYICI "=" expression
return_stmt      ::= "return" expression ";"
expr_stmt        ::= expression ";"

/* Expressions */
expression       ::= expression BINOP expression
                   | UNARYOP expression
                   | "(" expression ")"
                   | func_call
                   | LITERAL
                   | TANIMLAYICI

func_call        ::= TANIMLAYICI "(" arg_list? ")"
arg_list         ::= expression ("," expression)*

/* Terminals / Tokens */
BINOP            ::= "+" | "-" | "*" | "/" | "%" 
                   | "==" | "!=" | "<" | ">" | "<=" | ">=" 
                   | "&&" | "||"
UNARYOP          ::= "-" | "!"
LITERAL          ::= TAMSAYI | ONDALIKLI | "true" | "false" | STRING
TANIMLAYICI      ::= [a-zA-Z_][a-zA-Z0-9_]*
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