from symbol_table import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()

    def visit(self, node):
        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return
        
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for key, value in vars(node).items():
            if hasattr(value, '__dict__') or isinstance(value, list):
                self.visit(value)

    # --- Visit Methods ---

    def visit_Program(self, node):
        print("Analiz Basliyor...")
        self.visit(node.statements)
        # Print final Global Scope state
        self.symtab.print_current_scope("Global Scope") 
        print("Analiz Bitti.")

    def visit_Blok(self, node):
        self.symtab.enter_scope()
        self.visit(node.statements)
        # Print block scope before destroying it
        self.symtab.print_current_scope("Blok Scope") 
        self.symtab.exit_scope()

    def visit_DegiskenBildir(self, node):
        '''
        Eski logic

        # 1. Determine the type of the initial value
        val_type = 'unknown'
        if node.deger:
            val_type = self.visit(node.deger)
        
        # 2. Check if variable already exists in CURRENT scope
        if self.symtab.check_current_scope(node.isim):
            print(f"HATA: '{node.isim}' zaten tanimli!")
        else:
            # 3. Add to symbol table with the detected type
            self.symtab.add_symbol(node.isim, {'type': val_type, 'category': 'var'})        
        '''
        expr_type = 'unknown'
        # 1. Check if variable already exists in CURRENT scope
        if node.deger:
            expr_type = self.visit(node.deger)
            if expr_type != node.tip and expr_type != 'error':
                raise Exception(f"HATA: {node.isim} degiskeni '{node.tip}' turunde ama '{expr_type}' atandi.")
        
        # 2. Add to symbol table with the DECLARED type (no more 'unknown')
        if self.symtab.check_current_scope(node.isim):
            raise Exception(f"HATA: '{node.isim}' zaten tanimli!")
        else:
            self.symtab.add_symbol(node.isim, {'type': node.tip, 'category': 'var'})
        
    def visit_FonksiyonBildir(self, node):
        # 1. Extract parameter types to save in symbol table
        # node.parametreler is a list of tuples like [('int', 'x'), ('float', 'y')]
        param_types = [p[0] for p in node.parametreler]
        
        # 2. Register function with its SIGNATURE (param types)
        if self.symtab.check_current_scope(node.isim):
            print(f"HATA: '{node.isim}' fonksiyonu zaten tanimli!")
        else:
            # We save 'params': param_types so we can check them in a Call
            # We assume return type is 'void' or 'any' if not specified in your AST yet
            self.symtab.add_symbol(node.isim, {
                'type': 'function', 
                'category': 'func',
                'params': param_types,
                'return_type': node.return_type # node.return_type'a cevirdik
            })

        # 3. Enter INNER scope
        self.symtab.enter_scope()
        
        # Register parameters as variables inside the function
        for param_type, param_name in node.parametreler:
            self.symtab.add_symbol(param_name, {'type': param_type, 'category': 'param'})
        
        self.visit(node.govde) 
        
        self.symtab.print_current_scope(f"Fonksiyon: {node.isim}") 
        self.symtab.exit_scope()

    
    def visit_FonksiyonCall(self, node):
        # 1. Check if function is defined
        func_symbol = self.symtab.lookup(node.isim)
        if func_symbol is None:
            print(f"HATA: '{node.isim}' adinda bir fonksiyon bulunamadi!")
            return 'error'
        
        if func_symbol['category'] != 'func':
            print(f"HATA: '{node.isim}' bir fonksiyon degil!")
            return 'error'

        # 2. Check Argument Count
        expected_params = func_symbol['params']
        given_args = node.args # This is a list of expression nodes
        
        if len(given_args) != len(expected_params):
            print(f"HATA: '{node.isim}' fonksiyonu {len(expected_params)} parametre bekliyor, {len(given_args)} verildi.")
            return 'error'

        # 3. Check Argument Types
        for i, (arg_expr, expected_type) in enumerate(zip(given_args, expected_params)):
            arg_type = self.visit(arg_expr)
            
            if arg_type != expected_type and arg_type != 'error':
                print(f"HATA: '{node.isim}' fonksiyonunun {i+1}. parametresi '{expected_type}' olmali, '{arg_type}' verildi.")

        # Return the function's return type (e.g. 'void', 'int')
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
        # Visit children to get their types
        left_type = self.visit(node.sol)
        right_type = self.visit(node.sag)

        # Propagate errors
        if left_type == 'error' or right_type == 'error':
            return 'error'

        op = node.op

        # Arithmetic Operations
        if op in ['+', '-', '*', '/', '%']:
            if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                if left_type == 'float' or right_type == 'float':
                    return 'float'
                return 'int'
            else:
                print(f"HATA: Tip uyusmazligi! {left_type} {op} {right_type}. (Sayisal tur bekleniyor)")
                return 'error'
        
        # Comparison Operations
        elif op in ['<', '>', '<=', '>=', '==', '!=']:
            if left_type == right_type or (left_type in ['int', 'float'] and right_type in ['int', 'float']):
                return 'bool'
            else:
                print(f"HATA: Karsilastirma icin tipler uyumlu olmali: {left_type} vs {right_type}")
                return 'error'
        
        # Logical Operations
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

        # Type Inference: If variable was unknown/any (like params), we might allow updating it
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
    
# You can add visit_Atama, visit_BinaryOp, etc. here...