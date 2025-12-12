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
                found = False
                # Search from Top (Local) down to Bottom (Global)
                for frame in reversed(self.frames):
                    if arg in frame:
                        self.stack.append(frame[arg])
                        found = True
                        break
                if not found:
                    raise Exception(f"Runtime Error: '{arg}' tanimli degil.")

            elif opcode == 'STORE_VAR':
                if not self.stack: raise Exception("Stack Underflow")
                val = self.stack.pop()
                found = False
                
                # 1. Look for existing variable to UPDATE
                for frame in reversed(self.frames):
                    if arg in frame:
                        frame[arg] = val
                        found = True
                        # print(f" > Updated {arg} = {val}") # Debug
                        break
                
                # 2. If not found, create it in the CURRENT scope (or raise error)
                # In strict compilers, this should be an error (must use DEF_VAR), 
                # but for this homework, we can default to creating it in the top frame.
                if not found:
                     self.frames[-1][arg] = val
                     # print(f" > Created {arg} = {val}") # Debug

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
                if not self.return_stack:
                    break # Finished main program
                
                return_addr = self.return_stack.pop()
                
                # --- FIX: Destroy the function's local scope ---
                self.frames.pop()
                # -----------------------------------------------

                pc = return_addr

            elif opcode == 'ENTER_SCOPE':
                self.frames.append({}) # Push new empty scope

            elif opcode == 'EXIT_SCOPE':
                self.frames.pop()      # Destroy current scope

            elif opcode == 'DEF_VAR':
                # ALWAYS create in the current (top) frame.
                # Do not check parent frames. This shadows or initializes.
                if not self.stack: raise Exception("Stack Underflow")
                val = self.stack.pop()
                self.frames[-1][arg] = val
                print(f" > Defined {arg} = {val}")

            elif opcode == 'STORE_VAR':
                # STRICT UPDATE: Only update if it already exists in the chain.
                if not self.stack: raise Exception("Stack Underflow")
                val = self.stack.pop()
                found = False
                
                # Search from Top (Local) to Bottom (Global)
                for frame in reversed(self.frames):
                    if arg in frame:
                        frame[arg] = val
                        found = True
                        print(f" > Updated {arg} = {val}")
                        break
                
                if not found:
                    raise Exception(f"Runtime Error: Variable '{arg}' not declared (Use 'int {arg}').")

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