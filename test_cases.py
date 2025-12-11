import sys
from parser import parser
from ast_function import print_ast

def run_test(name, code, expect_success=True):
    print(f"Running Test: {name}")
    print("-" * 40)
    print(f"Code:\n{code.strip()}")
    print("-" * 40)
    
    try:
        result = parser.parse(code)
        
        if expect_success:
            if result:
                print("[OK] SUCCESS: AST Generated")
                print_ast(result)
            else:
                print("[FAIL] FAILURE: Parser returned None (Syntax Error?)")
        else:
            # We expected failure
            if result:
                print("[FAIL] FAILURE: Expected syntax error, but passed.")
            else:
                # Note: parser.py prints syntax errors to stdout usually
                print("[OK] SUCCESS: Syntax Error caught as expected.")

    except Exception as e:
        if expect_success:
            print(f"[FAIL] CRITICAL ERROR: {e}")
        else:
            print(f"[OK] SUCCESS: Exception caught: {e}")
    
    print("\n" + "="*60 + "\n")

# ==========================================
# TEST CASES
# ==========================================

# 1. Complex Logic (Fibonacci style)
test_valid_complex = """
def fib(n) {
    if (n <= 1) {
        return n;
    }
    return fib(n-1) + fib(n-2);
}

let result = 0;
for (let i = 0; i < 10; i = i + 1) {
    result = fib(i);
}
"""

# 2. Math and Precedence
test_valid_math = """
let x = 10 + 20 * 30;
let y = (10 + 20) * 30;
let z = -5;
let check = true && false || !true;
"""

# 3. Uninitialized Variable
test_valid_uninit = """
let x;
x = 100;
"""

# 4. Invalid Syntax (Missing semicolon)
test_invalid_syntax = """
let x = 10
let y = 20;
"""

# 5. Invalid Syntax (Bad function def)
test_invalid_func = """
def (a, b) {
    return 0;
}
"""

if __name__ == "__main__":
    print("STARTING TEST SUITE\n")
    
    run_test("Recursive Function & Loop", test_valid_complex, expect_success=True)
    run_test("Math Precedence & Logic", test_valid_math, expect_success=True)
    run_test("Uninitialized Variable", test_valid_uninit, expect_success=True)
    
    print("--- NEGATIVE TESTS (Expected Failures) ---\n")
    
    run_test("Missing Semicolon", test_invalid_syntax, expect_success=False)
    run_test("Malformed Function", test_invalid_func, expect_success=False)