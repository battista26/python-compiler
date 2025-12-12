class VirtualMachine:
    def __init__(self):
        self.stack = []      
        # self.variables is replaced by self.frames
        # frames[0] is Global Scope. frames[-1] is Current Function Scope.
        self.frames = [{}] 
        self.return_stack = [] 

    def run(self, instructions):
        print("--- VM Calisiyor ---")
        pc = 0 

        while pc < len(instructions):
            opcode, arg = instructions[pc]
            
            # Uncomment for debugging recursion
            # print(f"PC:{pc} | Op:{opcode} | Stack:{self.stack} | TopFrame:{self.frames[-1]}")

            if opcode == 'LOAD_CONST':
                self.stack.append(arg)
            
            elif opcode == 'LOAD_VAR':
                # 1. Check Local Scope (Top Frame)
                if arg in self.frames[-1]:
                    self.stack.append(self.frames[-1][arg])
                # 2. Check Global Scope (Bottom Frame)
                elif arg in self.frames[0]:
                    self.stack.append(self.frames[0][arg])
                else:
                    raise Exception(f"Runtime Error: '{arg}' tanimli degil.")

            elif opcode == 'STORE_VAR':
                if not self.stack: raise Exception("Stack Underflow")
                val = self.stack.pop()
                
                # Simple Logic: Always store in current (top) frame
                self.frames[-1][arg] = val
                print(f" > {arg} = {val}")

            elif opcode == 'ADD':
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a + b)
            elif opcode == 'SUB':
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a - b)
            elif opcode == 'MUL':
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a * b)
            elif opcode == 'DIV':
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a / b)
            
            elif opcode == 'COMPARE':
                b = self.stack.pop(); a = self.stack.pop()
                if arg == '==': self.stack.append(a == b)
                elif arg == '!=': self.stack.append(a != b)
                elif arg == '<': self.stack.append(a < b)
                elif arg == '>': self.stack.append(a > b)
                elif arg == '<=': self.stack.append(a <= b)
                elif arg == '>=': self.stack.append(a >= b)
                elif arg == '&&': self.stack.append(a and b)
                elif arg == '||': self.stack.append(a or b)
            
            elif opcode == 'JUMP_IF_FALSE':
                val = self.stack.pop()
                if not val:
                    pc = arg
                    continue 

            elif opcode == 'JUMP_ABSOLUTE':
                pc = arg
                continue

            elif opcode == 'CALL':
                target_addr = self.stack.pop()
                self.return_stack.append(pc)
                
                # NEW: Push a new empty frame for the function's local vars
                self.frames.append({}) 
                
                pc = target_addr
                continue

            elif opcode == 'RETURN':
                if not self.return_stack: break 
                
                return_addr = self.return_stack.pop()
                
                # NEW: Pop the function's frame (destroy local vars)
                self.frames.pop()
                
                pc = return_addr

            elif opcode == 'HALT':
                break

            elif opcode == 'PRINT':
                val = self.stack.pop()
                print(f"[OUTPUT] {val}")
            
            elif opcode == 'NEGATE':
                val = self.stack.pop()
                self.stack.append(-val)
                
            elif opcode == 'NOT':
                val = self.stack.pop()
                self.stack.append(not val)

            pc += 1 

        print("--- VM Bitti ---")
        # Print globals only
        print("Final Global Memory:", self.frames[0])