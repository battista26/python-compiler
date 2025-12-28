# In your main file or test runner:
from parser import parser, lexer
from ast_function import print_ast
from semantic_analyzer import SemanticAnalyzer
from bytecode_generator import BytecodeGenerator
from virtual_machine import VirtualMachine

code1 = """
let x = 10;
{
    let x = 20; # Shadowing check
    let y = 30;
    x = y + 1;
}
x = y; # ERROR: y is not defined here!
"""

code2 = """
int x = "hello";      # Type mismatch
y = 10;              # Undeclared variable
int x = 5;           # Redeclaration
"""

code3 = """
int x = 10;

int topla(int a, int b) {
    int x = 25;
    return a + b + x;
}
int sonuc = topla(5, 15); # 5 + 15 + 25 = 45

"""

code4 = """
int x = 10;
int num = 0;

while (x > 0) {
    x = x - 1;
    num = num + 1;
}
"""

if __name__ == "__main__":
    input_code = code4

    print("==========================================\n")
    print("--- Compiler Design Project ---\n")

    print("--- Source Code ---")
    print(input_code.strip())
    print("\n")

    print("--- Lexical Analysis ---")
    lexer.input(input_code)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(f"Tipi: {tok.type:<15} Degeri: {tok.value}")
    print("------------------------------------\n")

    print("\n--- Syntax Analysis (Parsing) ---")
    
    # Bunu yazmazsam lineno garip degerler veriyor
    lexer.lineno = 1

    ast = parser.parse(input_code)

    if ast:
        print("AST Tree Olusturuldu:")
        print_ast(ast)
    else:
        print("Syntax hatasi nedeniyle AST olusturulamadi.")
    
    print("\n--- Semantic Analysis ---")
    try:
        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)
        # Note: SemanticAnalyzer errorlari/scopelari internally tutuyor
    except Exception as e:
        print(f"KRITIK SEMANTIC HATASI: {e}")
        exit()
    print("----------------------------\n")

    print("\n--- Bytecode Generation ---")
    codegen = BytecodeGenerator()
    codegen.visit(ast)
    bytecode = codegen.get_bytecode()

    # instructionlari printleme
    for i, (op, arg) in enumerate(bytecode):
        arg_str = str(arg) if arg is not None else ""
        print(f"{i:<3}: {op:<15} {arg_str}")
    print("------------------------------\n")

    # dosya olarak kaydetme (opsiyonel)
    output_filename = "program.bytecode"
    with open(output_filename, "w") as f:
        for op, arg in bytecode:
            # We save it in a simple format: "OPCODE,ARGUMENT"
            # If arg is None, we just write "OPCODE"
            if arg is not None:
                f.write(f"{op},{arg}\n")
            else:
                f.write(f"{op}\n")
    print(f"\n[INFO] Bytecode'{output_filename}' dosyasina kaydedildi.")

    print("\n--- Virtual Machine Execution ---")
    vm = VirtualMachine()
    vm.run(bytecode)
    print("==========================================")
""" 
print("--- Parsing Code ---")

result = parser.parse(code3)
analyzer = SemanticAnalyzer()
analyzer.visit(result)

print("\n--- Bytecode Generation ---")
codegen = BytecodeGenerator()
codegen.visit(result)
bytecode = codegen.get_bytecode()

# Print the instructions nicely
for i, (op, arg) in enumerate(bytecode):
    print(f"{i}: {op} \t {arg if arg is not None else ''}")

print("\n--- Virtual Machine Bytecode ---")
vm = VirtualMachine()
vm.run(bytecode) """