class VirtualMachine:
    def __init__(self):
        self.stack = []      
        # self.variables yerine self.frames kullaniliyor
        # frames[0] Global Kapsamdir (Scope). frames[-1] Mevcut Fonksiyon Kapsamidir.
        self.frames = [{}] 
        self.return_stack = [] 

    def run(self, instructions):
        print("--- VM Calisiyor ---")
        pc = 0 

        while pc < len(instructions):
            opcode, arg = instructions[pc]
            
            # Ozyinelemeyi (recursion) hata ayiklamak (debug) icin yorumu kaldirin
            # print(f"PC:{pc} | Op:{opcode} | Stack:{self.stack} | TopFrame:{self.frames[-1]}")

            if opcode == 'LOAD_CONST':
                self.stack.append(arg)
            
            elif opcode == 'LOAD_VAR':
                found = False
                # En Ustten (Yerel) en Alta (Global) dogru ara
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
                
                # Guncellemek icin mevcut degiskeni ara
                for frame in reversed(self.frames):
                    if arg in frame:
                        frame[arg] = val
                        found = True
                        # print(f" > Updated {arg} = {val}") # Debug
                        break
                
                # Bulunamazsa, MEVCUT kapsamda olustur (veya hata firlat)
                # Kati derleyicilerde bu bir hata olmali (DEF_VAR kullanilmali), 
                # ancak bu odev icin ust cercevede olusturmayi varsayilan olarak kabul edebiliriz.
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
                
                # Fonksiyonun yerel degiskenleri icin yeni bos bir cerceve (frame) ekle
                self.frames.append({}) 
                
                pc = target_addr
                continue

            elif opcode == 'RETURN':
                if not self.return_stack:
                    break # Ana program bitti
                
                return_addr = self.return_stack.pop()
                
                # Fonksiyonun yerel kapsamini yok et
                self.frames.pop()

                pc = return_addr

            elif opcode == 'ENTER_SCOPE':
                self.frames.append({}) # Yeni bos kapsam ekle

            elif opcode == 'EXIT_SCOPE':
                self.frames.pop()      # Mevcut kapsami yok et

            elif opcode == 'DEF_VAR':
                # HER ZAMAN mevcut (ust) cercevede olustur.
                # Ust cerceveleri kontrol etme. Bu golgeleme (shadowing) yapar veya baslatir.
                if not self.stack: raise Exception("Stack Underflow")
                val = self.stack.pop()
                self.frames[-1][arg] = val
                print(f" > Defined {arg} = {val}")

            elif opcode == 'STORE_VAR':
                # Sadece zincirde zaten varsa guncelle.
                if not self.stack: raise Exception("Stack Underflow")
                val = self.stack.pop()
                found = False
                
                # En Ustten (Yerel) en Alta (Global) dogru ara
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
        # Sadece global hafizayi yazdir
        print("Final Global Memory:", self.frames[0])