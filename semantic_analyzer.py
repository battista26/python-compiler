from symbol_table import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()

    def visit(self, node):
        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return
        
        # Dinamik method cagirma, isme gore ziyaret eder
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    # Genel ziyaret metodu, visit methodu bulunamazsa alt dugumleri ziyaret eder
    def generic_visit(self, node):
        for key, value in vars(node).items():
            if hasattr(value, '__dict__') or isinstance(value, list):
                self.visit(value)

    # Visit methodlari

    def visit_Program(self, node):
        print("Analiz Basliyor...")
        self.visit(node.statements)
        # Global scope'u yazdir
        self.symtab.print_current_scope("Global Scope") 
        print("Analiz Bitti.")

    def visit_Blok(self, node):
        self.symtab.enter_scope()
        self.visit(node.statements)
        # Blok scope'u yazdir
        self.symtab.print_current_scope("Blok Scope") 
        self.symtab.exit_scope()

    def visit_DegiskenBildir(self, node):
        '''
        Eski logic
    
        val_type = 'unknown'
        if node.deger:
            val_type = self.visit(node.deger)
        
        if self.symtab.check_current_scope(node.isim):
            print(f"HATA: '{node.isim}' zaten tanimli!")
        else:
            # Scope'ta yoksa ekle
            self.symtab.add_symbol(node.isim, {'type': val_type, 'category': 'var'})        
        '''
        expr_type = 'unknown'
        # Degiskenin mevcut scope icinde zaten tanimli olup olmadigini kontrol et
        if node.deger:
            expr_type = self.visit(node.deger)
            if expr_type != node.tip and expr_type != 'error':
                raise Exception(f"HATA: {node.isim} degiskeni '{node.tip}' turunde ama '{expr_type}' atandi.")
        
        # Sembol tablosuna bildirilen degiskeni ekle (artik unknown degil, belirli tipte)
        if self.symtab.check_current_scope(node.isim):
            raise Exception(f"HATA: '{node.isim}' zaten tanimli!")
        else:
            self.symtab.add_symbol(node.isim, {'type': node.tip, 'category': 'var'})
        
    def visit_FonksiyonBildir(self, node):
        # Sembol tablosuna kaydetmek icin parametre tiplerini cikar
        # node.parametreler tuple listesi, mesela [('int', 'x'), ('float', 'y')]
        param_types = [p[0] for p in node.parametreler]
        
        # Fonksiyonu parametre tipleri ile birlikte kaydet
        if self.symtab.check_current_scope(node.isim):
            print(f"HATA: '{node.isim}' fonksiyonu zaten tanimli!")
        else:
            # 'params': param_types seklinde kaydediyoruz, cagrida kontrol edebiliriz
            #  AST'de henuz belirtilmediyse donus tipinin 'void' veya 'any' oldugunu varsayiyoruz
            self.symtab.add_symbol(node.isim, {
                'type': 'function', 
                'category': 'func',
                'params': param_types,
                'return_type': node.return_type # node.return_type'a cevirdik
            })

        # Inner scope'a giris
        self.symtab.enter_scope()
        
        # Parametreleri fonksiyon icinde degiskenler olarak kaydet
        for param_type, param_name in node.parametreler:
            self.symtab.add_symbol(param_name, {'type': param_type, 'category': 'param'})
        
        self.visit(node.govde) 
        
        self.symtab.print_current_scope(f"Fonksiyon: {node.isim}") 
        self.symtab.exit_scope()

    
    def visit_FonksiyonCall(self, node):
        # Fonksiyonun tanimli olup olmadigini kontrol et
        func_symbol = self.symtab.lookup(node.isim)
        if func_symbol is None:
            print(f"HATA: '{node.isim}' adinda bir fonksiyon bulunamadi!")
            return 'error'
        
        if func_symbol['category'] != 'func':
            print(f"HATA: '{node.isim}' bir fonksiyon degil!")
            return 'error'

        # Arguman sayisini kontrol et
        expected_params = func_symbol['params']
        given_args = node.args # Node listesi
        
        if len(given_args) != len(expected_params):
            print(f"HATA: '{node.isim}' fonksiyonu {len(expected_params)} parametre bekliyor, {len(given_args)} verildi.")
            return 'error'

        # Arguman tipi kontrolu
        for i, (arg_expr, expected_type) in enumerate(zip(given_args, expected_params)):
            arg_type = self.visit(arg_expr)
            
            if arg_type != expected_type and arg_type != 'error':
                print(f"HATA: '{node.isim}' fonksiyonunun {i+1}. parametresi '{expected_type}' olmali, '{arg_type}' verildi.")

        # Fonksiyonun return tipi (e.g. 'void', 'int')
        return func_symbol.get('return_type', 'void')
    
    def visit_IfStatement(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != 'bool' and condition_type != 'error':
            print(f"HATA: If kosulu 'bool' olmali, '{condition_type}' bulundu.")
        
        self.visit(node.true_blok)
        if node.else_blok:
            self.visit(node.else_blok)

    def visit_WhileStatement(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != 'bool' and condition_type != 'error':
            print(f"HATA: While kosulu 'bool' olmali, '{condition_type}' bulundu.")
        
        self.visit(node.govde)
        
    def visit_ForStatement(self, node):
        self.visit(node.init) # Visit initialization
        
        condition_type = self.visit(node.condition)
        if condition_type != 'bool' and condition_type != 'error':
             print(f"HATA: For kosulu 'bool' olmali, '{condition_type}' bulundu.")
             
        self.visit(node.update)
        self.visit(node.govde)


    def visit_Tanimlayici(self, node):
        symbol = self.symtab.lookup(node.isim)
        if symbol is None:
            raise Exception(f"HATA: '{node.isim}' tanimli degil!") 
        return symbol['type']

    def visit_Literal(self, node):
        return node.tip

    def visit_BinaryOp(self, node):
        # Tipleri almak icin children node'lari ziyaret et
        left_type = self.visit(node.sol)
        right_type = self.visit(node.sag)

        if left_type == 'error' or right_type == 'error':
            return 'error'

        op = node.op

        # Arithmetic
        if op in ['+', '-', '*', '/', '%']:
            if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                if left_type == 'float' or right_type == 'float':
                    return 'float'
                return 'int'
            else:
                print(f"HATA: Tip uyusmazligi! {left_type} {op} {right_type}. (Sayisal tur bekleniyor)")
                return 'error'
        
        # Karsilastirma
        elif op in ['<', '>', '<=', '>=', '==', '!=']:
            if left_type == right_type or (left_type in ['int', 'float'] and right_type in ['int', 'float']):
                return 'bool'
            else:
                print(f"HATA: Karsilastirma icin tipler uyumlu olmali: {left_type} vs {right_type}")
                return 'error'
        
        # Logic islemleri
        elif op in ['&&', '||']:
            if left_type == 'bool' and right_type == 'bool':
                return 'bool'
            else:
                print(f"HATA: Mantiksal islemler ({op}) sadece 'bool' turu ile calisir.")
                return 'error'
        
        return 'unknown'

    def visit_Atama(self, node):
        val_type = self.visit(node.deger)
        symbol = self.symtab.lookup(node.isim)
        
        if symbol is None:
            raise Exception(f"HATA: '{node.isim}' tanimli degil!")
        
        var_type = symbol['type']

        # Type Inference, variable unknown/any ise, guncellemeye izin var
        if var_type == 'unknown' or var_type == 'any':
            symbol['type'] = val_type
            # print(f"Bilgi: {node.isim} degiskeninin tipi '{val_type}' olarak guncellendi.")
        elif var_type != val_type and val_type != 'error':
            raise Exception(f"HATA: Tip uyusmazligi! '{node.isim}' ({var_type}) degiskenine '{val_type}' atanmaya calisildi.")
        
        return symbol['type']

    def visit_UnaryOp(self, node):
        expr_type = self.visit(node.expr)
        if expr_type == 'error': return 'error'

        if node.op == '!':
            if expr_type != 'bool':
                print(f"HATA: '!' operatoru sadece bool ile kullanilabilir. Gelen: {expr_type}")
                return 'error'
            return 'bool'
        elif node.op == '-':
            if expr_type not in ['int', 'float']:
                print(f"HATA: '-' operatoru sadece sayilarla kullanilabilir. Gelen: {expr_type}")
                return 'error'
            return expr_type
        
        return expr_type
    
if __name__ == "__main__":
    from lexer import lexer
    from parser import parser

    print("SEMANTIC ANALYSIS\n")

    # Düzgün Kod ve Sembol Tablosu
    print("TEST 1: Duzgun Kod ve Scope Yonetimi")
    code_valid = """
    string hatali = 34;
    """
    print("Verilen Kod:")
    print(code_valid.strip())
    print("-" * 60)
    
    try:
        # Parse -> AST
        lexer.input(code_valid)
        ast = parser.parse(code_valid)
        
        # Analyze -> Symbol Table
        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)
        print("\n[SUCCESS] Test 1 Passed: Symbol Table duzgun olusturuldu.")
        
    except Exception as e:
        print(f"[FAILED] Test 1: {e}")

    print("\n" + "="*60 + "\n")

    # Tip Hatasi Yakalama ---
    print("TEST 2: Tip Uyusmazligi Hatalarini Yakalama")
    code_error = """
    int sayi = 50;
    sayi = true;  # Tip uyusmazligi hatasi
    """
    print("Verilen Kod:")
    print(code_error.strip())
    print("-" * 60)
    
    try:
        # Parse -> AST
        lexer.input(code_error)
        ast = parser.parse(code_error)
        
        # Analyze (Should raise an exception)
        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)
        
    except Exception as e:
        # If we catch the error, the test is successful
        print("[SUCCESS] Test 2 Passed (Hata Basariyla Yakalandı):")
        print(f"   -> {e}")