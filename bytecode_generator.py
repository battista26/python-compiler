class BytecodeGenerator:
    def __init__(self):
        self.instructions = []

    def get_bytecode(self):
        return self.instructions

    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{node.__class__.__name__} method")

    # Visitor'lar

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)
    
        self.instructions.append(('HALT', None))  # Program sonu

    def visit_Blok(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_DegiskenBildir(self, node):
        # Format: int x = 5;
        # Degeri hesapla (push 5)
        if node.deger:
            self.visit(node.deger)
        else:
            # Deger yoksa, varsayilan olarak None/0 stack'e push et 
            self.instructions.append(('LOAD_CONST', 0))
        
        # 2. Degiskeni 'x' olarak kaydet
        self.instructions.append(('DEF_VAR', node.isim))

    def visit_Atama(self, node):
        # Format: x = 10;
        self.visit(node.deger) # Push 10
        self.instructions.append(('STORE_VAR', node.isim)) # Pop 10 -> save to x

    def visit_BinaryOp(self, node):
        # Format: 5 + 3
        # Sola push'la (5)
        self.visit(node.sol)
        # Saga push'la (3)
        self.visit(node.sag)
        
        # Operation Instruction'lari ekle
        if node.op == '+': self.instructions.append(('ADD', None))
        elif node.op == '-': self.instructions.append(('SUB', None))
        elif node.op == '*': self.instructions.append(('MUL', None))
        elif node.op == '/': self.instructions.append(('DIV', None))
        else:
            self.instructions.append(('COMPARE', node.op))
    
    def visit_IfStatement(self, node):
        # Condition degerlendir
        self.visit(node.condition)
        
        # False ise Else bloguna Jump
        jump_to_else_idx = len(self.instructions)
        self.instructions.append(('JUMP_IF_FALSE', None)) 
        
        # True blogu
        self.visit(node.true_blok)
        
        # Else blogundan Jump
        if node.else_blok:
            # True blogu bittiyse, Else blogunu atlamamiz gerekiyor
            jump_over_else_idx = len(self.instructions)
            self.instructions.append(('JUMP_ABSOLUTE', None))
        
        # 'JUMP_IF_FALSE' icin hedefi ayarla
        # False ise buraya atlayacak (Else baslangici)
        self.instructions[jump_to_else_idx] = ('JUMP_IF_FALSE', len(self.instructions))
        
        # Else blogu
        if node.else_blok:
            self.visit(node.else_blok)
            
            # 'JUMP_ABSOLUTE' icin hedefi ayarla
            # True blogu bittiyse, buraya atlayacak (Else sonu)
            self.instructions[jump_over_else_idx] = ('JUMP_ABSOLUTE', len(self.instructions))

    def visit_WhileStatement(self, node):
        start_idx = len(self.instructions) 
        
        self.visit(node.condition)
        
        jump_out_idx = len(self.instructions)
        self.instructions.append(('JUMP_IF_FALSE', None))
        
        self.visit(node.govde)
        
        # JUMP_ABSOLUTE olmasi lazim, cunku condition'a geri donuyoruz
        self.instructions.append(('JUMP_ABSOLUTE', start_idx)) 
        
        # jump_out icin duzeltme
        self.instructions[jump_out_idx] = ('JUMP_IF_FALSE', len(self.instructions))

    def visit_ForStatement(self, node):
        # Initialization
        # int i = 0; falan
        self.visit(node.init)

        # Loop baslangici
        # Her iterasyondan sonra condition kontrolu icin buraya donulecek.
        start_idx = len(self.instructions)

        # Condition degerlendir
        # i < 10 mesela
        self.visit(node.condition)

        # False ise cikis yap
        # Condition yanlis ise buraya atlayacak
        jump_out_idx = len(self.instructions)
        self.instructions.append(('JUMP_IF_FALSE', None))

        # Loop Govdesi
        # Ornek, { print(i); }
        self.visit(node.govde)

        # Update Adimi
        # i = i + 1, mesela
        # Kritik: Bu, govdeden SONRA ama basa donmeden ONCE calisir.
        self.visit(node.update)

        # Basa don
        self.instructions.append(('JUMP_ABSOLUTE', start_idx))

        # jump_out icin duzeltme
        # Hedef burda, dongu bittikten sonrasi
        after_loop_idx = len(self.instructions)
        self.instructions[jump_out_idx] = ('JUMP_IF_FALSE', after_loop_idx)


    def visit_FonksiyonBildir(self, node):
        # Function adini kaydet
        addr_const_idx = len(self.instructions)
        self.instructions.append(('LOAD_CONST', 0)) 
        self.instructions.append(('DEF_VAR', node.isim)) 

        # Govdeyi atla
        jump_over_idx = len(self.instructions)
        self.instructions.append(('JUMP_ABSOLUTE', None))

        # Function baslangici
        func_start_address = len(self.instructions)
        self.instructions[addr_const_idx] = ('LOAD_CONST', func_start_address)

        # Parametreler (DEF_VAR, CALL ile ekleniyor)
        for _, param_name in reversed(node.parametreler):
            self.instructions.append(('DEF_VAR', param_name))

        # Govde Kodu
        # self.visit(node.govde) kullanmadim cunku ENTER_SCOPE tetikliyor.
        # Bunun yerine, CALL frame'de kalmak icin ifadeleri manuel olarak dolasiyorum.
        if node.govde:
             for stmt in node.govde.statements:
                 self.visit(stmt)

        # Safety Return
        self.instructions.append(('LOAD_CONST', None))
        self.instructions.append(('RETURN', None))

        # Patch Jump
        after_func_idx = len(self.instructions)
        self.instructions[jump_over_idx] = ('JUMP_ABSOLUTE', after_func_idx)

    def visit_ReturnStatement(self, node):
        # Calculate the return value
        self.visit(node.deger)
        # Emit Return instruction
        self.instructions.append(('RETURN', None))

    def visit_FonksiyonCall(self, node):
        # Argumanlari stack'e at
        for arg in node.args:
            self.visit(arg)
        
        # Function adresini yukle
        self.instructions.append(('LOAD_VAR', node.isim))
        
        # Instruction'lari cagir
        self.instructions.append(('CALL', None))

    def visit_UnaryOp(self, node):
        # Expression'i stack'e at
        self.visit(node.expr)
        
        # Operasyonu ekle
        if node.op == '-':
            self.instructions.append(('NEGATE', None))
        elif node.op == '!':
            self.instructions.append(('NOT', None))

    def visit_Literal(self, node):
        self.instructions.append(('LOAD_CONST', node.deger))

    def visit_Tanimlayici(self, node):
        self.instructions.append(('LOAD_VAR', node.isim))
        
    def visit_ExprStmt(self, node):
        # '5+5;' gibi bir ifade varsa, hesapliyoruz
        # Ama genellikle pop yaparız ki stack temiz kalsın.
        # Simdilik, sonucu gorebilmeniz icin yazdiriyorum
        self.visit(node) # AST wrapper varsa node.expression olmali
        self.instructions.append(('PRINT', None))

# Add this to the bottom of bytecode_generator.py
if __name__ == "__main__":
    from lexer import lexer
    from parser import parser
    
    # Example: A Loop with Math (Showcases Jumps and Stack)
    code = """
    int i = 0;
    while (i < 3) {
        i = i + 1;
    }
    """
    
    print("BYTECODE GENERATION\n")
    print(f"Verilen Kod:\n{code.strip()}\n")
    print("-" * 60)
    print(f"{'IDX':<6} {'OPCODE':<20} {'OPERAND':<10}")
    print("-" * 60)

    try:
        # Parse
        lexer.input(code)
        ast = parser.parse(code)
        
        # Bytecode Uret
        generator = BytecodeGenerator()
        generator.visit(ast)
        bytecode = generator.get_bytecode()
        
        # Instruction'lari Yazdir
        for i, (opcode, operand) in enumerate(bytecode):
            operand_str = str(operand) if operand is not None else ""
            print(f"{i:<6} {opcode:<20} {operand_str:<10}")
            
    except Exception as e:
        print(f"Error: {e}")