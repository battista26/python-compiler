from parser import parser
from lexer import lexer

def run_test(code):
    print("-" * 20)
    print(f"Code:\n{code.strip()}")
    
    # --- FIX IS HERE ---
    # Reset line number counter to 1 before every new parse
    lexer.lineno = 1 
    # -------------------

    try:
        # Pass the lexer explicitly to ensure it uses the reset one
        result = parser.parse(code, lexer=lexer)
        print("Result:", result)
    except Exception as e:
        print(e)

# Example usage
code1 = "int x = 10;"
run_test(code1) # Ends at line 1

code4 = """
floating x = 10.0;
"""
run_test(code4) # Now this will correctly say line 2 (because of the initial newline)