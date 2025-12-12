import sys
from parser import parser, lexer
from semantic_analyzer import SemanticAnalyzer
from bytecode_generator import BytecodeGenerator
from virtual_machine import VirtualMachine

# Helper to clear previous state
def reset_compiler():
    # We might need to reset lexer lineno if it persists, 
    # but usually creating new instances of Analyzer/VM is enough.
    lexer.lineno = 1

def run_test(name, code, test_type="valid", expected_vars=None):
    """
    test_type options: 
      - "valid": Expects successful execution. Checks final VM variables.
      - "semantic_error": Expects SemanticAnalyzer to raise an exception.
      - "syntax_error": Expects Parser to fail.
    """
    print(f"TEST: {name}")
    print("-" * 50)
    # print(f"Code:\n{code.strip()}\n")
    
    reset_compiler()

    # --- 1. PARSING ---
    try:
        ast = parser.parse(code)
    except Exception as e:
        if test_type == "syntax_error":
            print(f"[OK] Syntax Error caught as expected: {e}")
            print("="*50 + "\n")
            return
        else:
            print(f"[FAIL] Parser Crashed: {e}")
            return

    if test_type == "syntax_error":
        if ast is None:
            print("[OK] Syntax Error caught as expected.")
        else:
            print("[FAIL] Expected Syntax Error, but parsed successfully.")
        print("="*50 + "\n")
        return

    if ast is None:
        print("[FAIL] Parsing failed (returned None).")
        print("="*50 + "\n")
        return

    # --- 2. SEMANTICS ---
    analyzer = SemanticAnalyzer()
    try:
        analyzer.visit(ast)
    except Exception as e:
        if test_type == "semantic_error":
            print(f"[OK] Semantic Error caught: {e}")
        else:
            print(f"[FAIL] Unexpected Semantic Error: {e}")
        print("="*50 + "\n")
        return

    if test_type == "semantic_error":
        print("[FAIL] Expected Semantic Error, but analysis passed.")
        print("="*50 + "\n")
        return

    # --- 3. CODE GEN ---
    try:
        codegen = BytecodeGenerator()
        codegen.visit(ast)
        bytecode = codegen.get_bytecode()
    except Exception as e:
        print(f"[FAIL] Code Generation Error: {e}")
        return

    # --- 4. VM EXECUTION ---
    vm = VirtualMachine()
    try:
        # Suppress VM print output to keep test logs clean (optional)
        # sys.stdout = open('os.devnull', 'w') 
        vm.run(bytecode)
        # sys.stdout = sys.__stdout__ # Restore print
    except Exception as e:
        # sys.stdout = sys.__stdout__
        print(f"[FAIL] Runtime/VM Error: {e}")
        return

    # --- 5. VERIFICATION ---
    if expected_vars:
        all_match = True
        for var_name, expected_val in expected_vars.items():
            actual_val = vm.frames[0].get(var_name)
            if actual_val != expected_val:
                print(f"[FAIL] Variable '{var_name}' mismatch! Expected {expected_val}, got {actual_val}")
                all_match = False
        
        if all_match:
            print(f"[OK] Test Passed. Final State Verified.")
    else:
        print(f"[OK] Test Passed (No state check).")
    
    print("="*50 + "\n")


# ==========================================
# TEST SUITE (15 Cases)
# ==========================================

if __name__ == "__main__":
    print("STARTING 15-TEST SUITE...\n")

    # --- GROUP A: Basic Data Types & Math ---
    
    code_1 = """
    int x = 10 + 5 * 2;   # Should be 20
    int y = (10 + 5) * 2; # Should be 30
    """
    run_test("1. Integer Math & Precedence", code_1, "valid", {"x": 20, "y": 30})

    code_2 = """
    float pi = 3.14;
    float r = 2.0;
    float area = pi * r * r; # 12.56
    """
    run_test("2. Floating Point Arithmetic", code_2, "valid", {"area": 12.56})

    code_3 = """
    bool a = true;
    bool b = false;
    bool c = a && b;  # False
    bool d = a || b;  # True
    bool e = !a;      # False
    """
    run_test("3. Boolean Logic (AND/OR/NOT)", code_3, "valid", {"c": False, "d": True, "e": False})

    code_4 = """
    int a = 10;
    int b = -a;      # -10
    int c = -(-5);   # 5
    """
    run_test("4. Unary Minus Operator", code_4, "valid", {"b": -10, "c": 5})

    code_5 = """
    string s1 = "Hello";
    string s2 = "World";
    """
    run_test("5. String Literals", code_5, "valid", {"s1": "Hello", "s2": "World"})


    # --- GROUP B: Control Flow ---

    code_6 = """
    int x = 10;
    int y = 0;
    if (x > 5) {
        y = 1;
    } else {
        y = 2;
    }
    """
    run_test("6. If-Else Control Flow", code_6, "valid", {"y": 1})

    code_7 = """
    int i = 5;
    int fact = 1;
    while (i > 0) {
        fact = fact * i;
        i = i - 1;
    }
    """
    run_test("7. While Loop (Factorial)", code_7, "valid", {"fact": 120, "i": 0})

    code_8 = """
    int sum = 0;
    int i;
    for (i = 0; i < 5; i = i + 1) {
        sum = sum + i;
    }
    """
    run_test("8. For Loop (Summation)", code_8, "valid", {"sum": 10})


    # --- GROUP C: Functions & Scope ---

    code_9 = """
    int add(int a, int b) {
        return a + b;
    }
    int res = add(10, 20);
    """
    run_test("9. Function Call (Arguments & Return)", code_9, "valid", {"res": 30})

    code_10 = """
    int fib(int n) {
        if (n <= 1) { return n; }
        return fib(n-1) + fib(n-2);
    }
    int res = fib(6); # Should be 8
    """
    run_test("10. Recursive Function (Fibonacci)", code_10, "valid", {"res": 8})

    code_11 = """
    int x = 10;
    {
        int x = 20; # Shadowing outer x
        x = x + 1;  # 21
    }
    # Blok scope'u 
    """
    run_test("11. Scope Shadowing (Block Scope)", code_11, "valid", {"x": 10})


    # --- GROUP D: Negative Tests (Expected Failures) ---

    code_12 = """
    int x = "Hello";
    """
    run_test("12. Semantic: Type Mismatch (Int = String)", code_12, "semantic_error")

    code_13 = """
    x = 5;
    """
    run_test("13. Semantic: Undeclared Variable", code_13, "semantic_error")

    code_14 = """
    int x = 5;
    int x = 10;
    """
    run_test("14. Semantic: Variable Redeclaration", code_14, "semantic_error")

    code_15 = """
    int x = 10
    int y = 20;
    """
    run_test("15. Syntax: Missing Semicolon", code_15, "syntax_error")