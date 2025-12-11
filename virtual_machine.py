class VirtualMachine:
    def __init__(self):
        self.stack = []      
        self.variables = {}  

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
            
            elif opcode == 'PRINT':
                val = self.stack.pop()
                print(f"[OUTPUT] {val}")

            pc += 1 

        print("--- VM Bitti ---")
        print("Final Memory State:", self.variables)