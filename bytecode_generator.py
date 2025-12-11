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

    # --- Visitors ---

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Blok(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_DegiskenBildir(self, node):
        # Format: int x = 5;
        # 1. Calculate the value (push 5)
        if node.deger:
            self.visit(node.deger)
        else:
            # If no value, push None/0 default
            self.instructions.append(('LOAD_CONST', 0))
        
        # 2. Store it in variable 'x'
        self.instructions.append(('STORE_VAR', node.isim))

    def visit_Atama(self, node):
        # Format: x = 10;
        self.visit(node.deger) # Push 10
        self.instructions.append(('STORE_VAR', node.isim)) # Pop 10 -> save to x

    def visit_BinaryOp(self, node):
        # Format: 5 + 3
        # 1. Push Left (5)
        self.visit(node.sol)
        # 2. Push Right (3)
        self.visit(node.sag)
        
        # 3. Add Operation Instruction
        if node.op == '+': self.instructions.append(('ADD', None))
        elif node.op == '-': self.instructions.append(('SUB', None))
        elif node.op == '*': self.instructions.append(('MUL', None))
        elif node.op == '/': self.instructions.append(('DIV', None))
        else:
            self.instructions.append(('COMPARE', node.op))
    
    def visit_IfStatement(self, node):
        # 1. Evaluate Condition
        self.visit(node.condition)
        
        # 2. Jump to Else if False
        jump_to_else_idx = len(self.instructions)
        self.instructions.append(('JUMP_IF_FALSE', None)) 
        
        # 3. True Block
        self.visit(node.true_blok)
        
        # --- NEW: Jump over the Else block ---
        if node.else_blok:
            # If we finished the True block, we must skip the Else block
            jump_over_else_idx = len(self.instructions)
            self.instructions.append(('JUMP_ABSOLUTE', None))
        
        # 4. Set Target for 'JUMP_IF_FALSE'
        # If false, we land here (start of else block, or end of if)
        self.instructions[jump_to_else_idx] = ('JUMP_IF_FALSE', len(self.instructions))
        
        # 5. Else Block
        if node.else_blok:
            self.visit(node.else_blok)
            
            # 6. Set Target for 'JUMP_ABSOLUTE'
            # If we finished True block, we land here (end of else)
            self.instructions[jump_over_else_idx] = ('JUMP_ABSOLUTE', len(self.instructions))

    def visit_WhileStatement(self, node):
        start_idx = len(self.instructions) 
        
        self.visit(node.condition)
        
        jump_out_idx = len(self.instructions)
        self.instructions.append(('JUMP_IF_FALSE', None))
        
        self.visit(node.govde)
        
        # This MUST be JUMP_ABSOLUTE
        self.instructions.append(('JUMP_ABSOLUTE', start_idx)) 
        
        # Patch the jump_out
        self.instructions[jump_out_idx] = ('JUMP_IF_FALSE', len(self.instructions))

    def visit_Literal(self, node):
        self.instructions.append(('LOAD_CONST', node.deger))

    def visit_Tanimlayici(self, node):
        self.instructions.append(('LOAD_VAR', node.isim))
        
    def visit_ExprStmt(self, node):
        # If you have an expression statement like '5+5;', we calculate it 
        # but then we usually want to pop it so the stack stays clean.
        # For now, let's print it so you can see the result!
        self.visit(node) # Should be node.expression if your AST has that wrapper
        self.instructions.append(('PRINT', None))