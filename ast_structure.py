# AST temel sinif
class AST:
    def __repr__(self):
        return f"<{self.__class__.__name__}>"

# AST'de en tepedeki node
class Program(AST):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"

# {} gibi bloklari temsil eden sinif
class Blok(AST):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Blok({self.statements})"

# Bildirme(declaration), fonksiyon(function) ve atamalar(assignment)

# let x = 10
# AST [DegiskenBildir(isim='x', deger=Literal(10, type_='int'))]
# let artik kullanilmiyor, artik tip belirterek de bildirebiliyoruz.
class DegiskenBildir(AST):
    def __init__(self, isim, tip, deger):
        self.isim = isim  # Tanımlayici(identifier) string
        self.tip = tip    # Tip string, e.g., 'int', 'float'
        self.deger = deger # Expression node
    def __repr__(self):
        return f"DegiskenBildir(isim='{self.isim}', tip={self.tip}, deger={self.deger})"
# def fonksiyonum(a, b) { ... }
# AST [FonksiyonBildir(isim='fonksiyonum', parametreler=['a', 'b'], govde=Blok(...))]
class FonksiyonBildir(AST):
    def __init__(self, isim, return_type, parametreler, govde):
        self.isim = isim
        self.return_type = return_type  # Simdilik void, AST'de return type eklenirse degistirilebilir
        self.parametreler = parametreler  # Parametreler
        self.govde = govde      # Blok node
    def __repr__(self):
        return f"FonksiyonBildir(isim='{self.isim}', return_type={self.return_type}, parametreler={self.parametreler}, govde={self.govde})"

# x = 20
# AST [Atama(isim='x', deger=Literal(20, type_='int'))]
class Atama(AST):
    def __init__(self, isim, deger):
        self.isim = isim
        self.deger = deger

    def __repr__(self):
        return f"Atama(isim='{self.isim}', deger={self.deger})"

# If, While, For, Return statementlari

class IfStatement(AST):
    def __init__(self, condition, true_blok, else_blok=None):
        self.condition = condition
        self.true_blok = true_blok
        self.else_blok = else_blok

    def __repr__(self):
        return f"If({self.condition}, {self.true_blok}, else={self.else_blok})"

class WhileStatement(AST):
    def __init__(self, condition, govde):
        self.condition = condition
        self.govde = govde

    def __repr__(self):
        return f"While({self.condition}, govde={self.govde})"

class ForStatement(AST):
    def __init__(self, init, condition, update, govde):
        self.init = init         # e.g., let i = 0
        self.condition = condition # e.g., i < 10
        self.update = update     # e.g., i = i + 1
        self.govde = govde

    def __repr__(self):
        return f"For(init={self.init}, cond={self.condition}, update={self.update}, govde={self.govde})"

class ReturnStatement(AST):
    def __init__(self, deger):
        self.deger = deger

    def __repr__(self):
        return f"Return({self.deger})"

# Expressionlar

# +, -, *, /, %, >, <, ==, &&, || operasyonlari için sinif
class BinaryOp(AST):
    def __init__(self, sol, op, sag):
        self.sol = sol
        self.op = op  # The token string, e.g., '+', '==', '&&'
        self.sag = sag

    def __repr__(self):
        return f"BinOp({self.sol} {self.op} {self.sag})"

# -x, !y gibi unary operasyonlar için sinif
class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.expr})"

# Fonksiyon cagrilari için sinif
class FonksiyonCall(AST):
    def __init__(self, isim, args):
        self.isim = isim
        self.args = args  # Expression node listesi

    def __repr__(self):
        return f"Call(name='{self.isim}', args={self.args})"

class Literal(AST):
    def __init__(self, deger, tip):
        self.deger = deger
        self.tip = tip # 'int', 'float', 'bool'

    def __repr__(self):
        return f"Literal({self.deger}, type={self.tip})"

class Tanimlayici(AST):
    def __init__(self, isim):
        self.isim = isim

    def __repr__(self):
        return f"Id({self.isim})"