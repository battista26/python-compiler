class VirtualMachine:
    def __init__(self):
        self.stack = []      
        self.variables = {}
        self.return_stack = []

    def run(self, instructions):
        print("--- VM Calisiyor ---")
        pc = 0 # Program Counter

        while pc < len(instructions):
            opcode, arg = instructions[pc]
            
            # Debugging: Uncomment to see the heartbeat of the VM
            # print(f"PC:{pc} | Op:{opcode} Arg:{arg} | Stack:{self.stack}")

            if opcode == 'LOAD_CONST':
                self.stack.append(arg)
            
            elif opcode == 'LOAD_VAR':
                if arg in self.variables:
                    self.stack.append(self.variables[arg])
                else:
                    raise Exception(f"Runtime Error: '{arg}' tanimli degil.")

            elif opcode == 'STORE_VAR':
                # FIX 1: Make sure we POP the value
                val = self.stack.pop()
                self.variables[arg] = val
                print(f" > {arg} = {val}")

            elif opcode == 'ADD':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)

            elif opcode == 'SUB':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)

            elif opcode == 'MUL':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)

            elif opcode == 'DIV':
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b)

            elif opcode == 'COMPARE':
                # FIX 2: Order matters! b is popped first (right side)
                b = self.stack.pop()
                a = self.stack.pop()
                
                if arg == '==': self.stack.append(a == b)
                elif arg == '!=': self.stack.append(a != b)
                elif arg == '<': self.stack.append(a < b)
                elif arg == '>': self.stack.append(a > b) # num > 0
                elif arg == '<=': self.stack.append(a <= b)
                elif arg == '>=': self.stack.append(a >= b)
                elif arg == '&&': self.stack.append(a and b)
                elif arg == '||': self.stack.append(a or b)
                else:
                    raise Exception(f"Runtime Error: Bilinmeyen karsilastirma operatoru '{arg}'.")

            elif opcode == 'JUMP_IF_FALSE':
                # FIX 3: MUST POP the condition. 
                # If you just peek (stack[-1]), the stack grows forever.
                val = self.stack.pop() 
                
                # FIX 4: Use 'not val' to catch False, 0, or None safely
                if not val:
                    pc = arg
                    continue # Skip the pc += 1 at bottom

            elif opcode == 'JUMP_ABSOLUTE':
                pc = arg
                continue # Skip the pc += 1 at bottom

            elif opcode == 'CALL':
                # 1. Pop the target address (pushed by LOAD_VAR function_name)
                target_addr = self.stack.pop()
                
                # 2. Save current PC (where we are now) so we can return later
                self.return_stack.append(pc)
                
                # 3. Jump to function
                pc = target_addr
                continue

            elif opcode == 'RETURN':
                # 1. Check if we have somewhere to return to
                if not self.return_stack:
                     # If stack empty, we finished the main program (or function finished)
                     break
                
                # 2. Restore the old PC
                return_addr = self.return_stack.pop()
                pc = return_addr
                # We don't 'continue' here because we want to move to the NEXT instruction
                # after the Call.

            elif opcode == 'NEGATE':
                val = self.stack.pop()
                self.stack.append(-val)

            elif opcode == 'NOT':
                val = self.stack.pop()
                self.stack.append(not val)

            elif opcode == 'HALT':
                print("Program sonlandi.")
                break
            
            elif opcode == 'PRINT':
                val = self.stack.pop()
                print(f"[OUTPUT] {val}")

            pc += 1 

        print("--- VM Bitti ---")
        print("Final Memory State:", self.variables)