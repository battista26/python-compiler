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
    
        self.instructions.append(('HALT', None))  # Program sonu

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

    def visit_ForStatement(self, node):
        # 1. Initialization (Run once)
        # Example: int i = 0;
        self.visit(node.init)

        # 2. Mark the Start of the Loop
        # We will jump back here after every iteration to check the condition.
        start_idx = len(self.instructions)

        # 3. Evaluate Condition
        # Example: i < 10
        self.visit(node.condition)

        # 4. Jump Out if False
        # If condition is false, jump to the end (we fix the target later)
        jump_out_idx = len(self.instructions)
        self.instructions.append(('JUMP_IF_FALSE', None))

        # 5. Loop Body
        # Example: { print(i); }
        self.visit(node.govde)

        # 6. Update Step
        # Example: i = i + 1
        # Crucial: This runs AFTER the body, but BEFORE jumping back.
        self.visit(node.update)

        # 7. Jump Back to Start
        self.instructions.append(('JUMP_ABSOLUTE', start_idx))

        # 8. Fix the Jump Out Target
        # The target is right here, after the loop finishes.
        after_loop_idx = len(self.instructions)
        self.instructions[jump_out_idx] = ('JUMP_IF_FALSE', after_loop_idx)


    def visit_FonksiyonBildir(self, node):
        # 1. Register the function name BEFORE skipping the body.
        # We don't know the body address yet, so we use a placeholder (0) for now.
        addr_const_idx = len(self.instructions)
        self.instructions.append(('LOAD_CONST', 0)) 
        self.instructions.append(('STORE_VAR', node.isim)) # Now this runs immediately!

        # 2. Skip the body (so it doesn't run automatically)
        jump_over_idx = len(self.instructions)
        self.instructions.append(('JUMP_ABSOLUTE', None))

        # 3. Mark the start of the function body
        func_start_address = len(self.instructions)

        # 4. BACKPATCH: Now we know the address, update step 1
        self.instructions[addr_const_idx] = ('LOAD_CONST', func_start_address)

        # 5. Handle Parameters (These store values passed by the caller)
        # We pop them in reverse order because Stack is LIFO
        for _, param_name in reversed(node.parametreler):
            self.instructions.append(('STORE_VAR', param_name))

        # 6. Generate Body Code
        self.visit(node.govde)

        # 7. Safety Return (in case user forgot)
        self.instructions.append(('LOAD_CONST', None))
        self.instructions.append(('RETURN', None))

        # 8. Fix the Jump Over target
        after_func_idx = len(self.instructions)
        self.instructions[jump_over_idx] = ('JUMP_ABSOLUTE', after_func_idx)

    def visit_ReturnStatement(self, node):
        # Calculate the return value
        self.visit(node.deger)
        # Emit Return instruction
        self.instructions.append(('RETURN', None))

    def visit_FonksiyonCall(self, node):
        # 1. Push Arguments onto the stack
        for arg in node.args:
            self.visit(arg)
        
        # 2. Load the Function Address
        self.instructions.append(('LOAD_VAR', node.isim))
        
        # 3. Call Instruction (Jumps to the address on stack)
        self.instructions.append(('CALL', None))

    def visit_UnaryOp(self, node):
        # 1. Push the expression value onto the stack
        self.visit(node.expr)
        
        # 2. Apply the operation
        if node.op == '-':
            self.instructions.append(('NEGATE', None))
        elif node.op == '!':
            self.instructions.append(('NOT', None))

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