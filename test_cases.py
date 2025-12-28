import sys
from parser import parser, lexer
from semantic_analyzer import SemanticAnalyzer
from bytecode_generator import BytecodeGenerator
from virtual_machine import VirtualMachine

# Onceki durumu temizlemek icin yardimci fonksiyon
def reset_compiler():
    # Lexer satir numarasini (lineno) sifirlamamiz gerekebilir,
    # ancak genellikle yeni Analyzer/VM ornekleri olusturmak yeterlidir.
    lexer.lineno = 1

def run_test(name, code, test_type="valid", expected_vars=None):
    """
    test_type secenekleri: 
      - "valid": Basarili calisma beklenir. Final VM degiskenlerini kontrol eder.
      - "semantic_error": SemanticAnalyzer'in bir istisna (exception) firlatmasi beklenir.
      - "syntax_error": Parser'in hata vermesi beklenir.
    """
    print(f"TEST: {name}")
    print("-" * 50)
    # print(f"Kod:\n{code.strip()}\n")
    
    reset_compiler()

    # --- 1. PARSING (AYRISTIRMA) ---
    try:
        ast = parser.parse(code)
    except Exception as e:
        if test_type == "syntax_error":
            print(f"[TAMAM] Syntax Hatasi beklendigi gibi yakalandi: {e}")
            print("="*50 + "\n")
            return
        else:
            print(f"[HATA] Parser Coktu: {e}")
            return

    if test_type == "syntax_error":
        if ast is None:
            print("[TAMAM] Syntax Hatasi beklendigi gibi yakalandi.")
        else:
            print("[HATA] Syntax Hatasi bekleniyordu ama basariyla ayristirildi.")
        print("="*50 + "\n")
        return

    if ast is None:
        print("[HATA] Ayristirma basarisiz (None dondu).")
        print("="*50 + "\n")
        return

    # --- 2. SEMANTICS (ANLAM ANALIZI) ---
    analyzer = SemanticAnalyzer()
    try:
        analyzer.visit(ast)
    except Exception as e:
        if test_type == "semantic_error":
            print(f"[TAMAM] Semantik Hata yakalandi: {e}")
        else:
            print(f"[HATA] Beklenmeyen Semantik Hata: {e}")
        print("="*50 + "\n")
        return

    if test_type == "semantic_error":
        print("[HATA] Semantik Hata bekleniyordu ama analiz gecti.")
        print("="*50 + "\n")
        return

    # --- 3. CODE GEN (KOD URETIMI) ---
    try:
        codegen = BytecodeGenerator()
        codegen.visit(ast)
        bytecode = codegen.get_bytecode()
    except Exception as e:
        print(f"[HATA] Kod Uretim Hatasi: {e}")
        return

    # --- 4. VM EXECUTION (VM CALISTIRMA) ---
    vm = VirtualMachine()
    try:
        # Test loglarini temiz tutmak icin VM ciktilarini (print) gizleyebilirsiniz (opsiyonel)
        # sys.stdout = open('os.devnull', 'w') 
        vm.run(bytecode)
        # sys.stdout = sys.__stdout__ # Print'i geri yukle
    except Exception as e:
        # sys.stdout = sys.__stdout__
        print(f"[HATA] Calisma Zamani/VM Hatasi: {e}")
        return

    # --- 5. VERIFICATION (DOGRULAMA) ---
    if expected_vars:
        all_match = True
        for var_name, expected_val in expected_vars.items():
            actual_val = vm.frames[0].get(var_name)
            if actual_val != expected_val:
                print(f"[HATA] Degisken '{var_name}' uyusmazligi! Beklenen {expected_val}, gelen {actual_val}")
                all_match = False
        
        if all_match:
            print(f"[TAMAM] Test Gecti. Son Durum Dogrulandi.")
    else:
        print(f"[TAMAM] Test Gecti (Durum kontrolu yok).")
    
    print("="*50 + "\n")


# ==========================================
# TEST SUITE (15 Cases)
# ==========================================

if __name__ == "__main__":
    print("15 TESTLIK SUITE BASLATILIYOR...\n")

    # --- GRUP A: Temel Veri Tipleri & Matematik ---
    
    code_1 = """
    int x = 10 + 5 * 2;   # 20 olmali
    int y = (10 + 5) * 2; # 30 olmali
    """
    run_test("1. Tamsayi Matematigi & Oncelik", code_1, "valid", {"x": 20, "y": 30})

    code_2 = """
    float pi = 3.14;
    float r = 2.0;
    float area = pi * r * r; # 12.56
    """
    run_test("2. Kayan Noktali (Float) Aritmetik", code_2, "valid", {"area": 12.56})

    code_3 = """
    bool a = true;
    bool b = false;
    bool c = a && b;  # False
    bool d = a || b;  # True
    bool e = !a;      # False
    """
    run_test("3. Mantiksal Islemler (VE/VEYA/DEGIL)", code_3, "valid", {"c": False, "d": True, "e": False})

    code_4 = """
    int a = 10;
    int b = -a;      # -10
    int c = -(-5);   # 5
    """
    run_test("4. Unary Eksi Operatoru", code_4, "valid", {"b": -10, "c": 5})

    code_5 = """
    string s1 = "Merhaba";
    string s2 = "Dunya";
    """
    run_test("5. String Literalleri", code_5, "valid", {"s1": "Merhaba", "s2": "Dunya"})


    # --- GRUP B: Akis Kontrolu (Control Flow) ---

    code_6 = """
    int x = 10;
    int y = 0;
    if (x > 5) {
        y = 1;
    } else {
        y = 2;
    }
    """
    run_test("6. If-Else Akis Kontrolu", code_6, "valid", {"y": 1})

    code_7 = """
    int i = 5;
    int fact = 1;
    while (i > 0) {
        fact = fact * i;
        i = i - 1;
    }
    """
    run_test("7. While Dongusu (Faktoriyel)", code_7, "valid", {"fact": 120, "i": 0})

    code_8 = """
    int sum = 0;
    int i;
    for (i = 0; i < 5; i = i + 1) {
        sum = sum + i;
    }
    """
    run_test("8. For Dongusu (Toplam)", code_8, "valid", {"sum": 10})


    # --- GRUP C: Fonksiyonlar & Kapsam (Scope) ---

    code_9 = """
    int add(int a, int b) {
        return a + b;
    }
    int res = add(10, 20);
    """
    run_test("9. Fonksiyon Cagrisi (Argumanlar & Donus)", code_9, "valid", {"res": 30})

    code_10 = """
    int fib(int n) {
        if (n <= 1) { return n; }
        return fib(n-1) + fib(n-2);
    }
    int res = fib(6); # 8 olmali
    """
    run_test("10. Ozyinelemeli (Recursive) Fonksiyon (Fibonacci)", code_10, "valid", {"res": 8})

    code_11 = """
    int x = 10;
    {
        int x = 20; # Disaridaki x'i golgeliyor (Shadowing)
        x = x + 1;  # 21
    }
    # Blok kapsami bitti
    """
    run_test("11. Kapsam Golgeleme (Blok Kapsami)", code_11, "valid", {"x": 10})


    # --- GRUP D: Negatif Testler (Beklenen Hatalar) ---

    code_12 = """
    int x = "Hello";
    """
    run_test("12. Semantik: Tip Uyusmazligi (Int = String)", code_12, "semantic_error")

    code_13 = """
    x = 5;
    """
    run_test("13. Semantik: Tanimlanmamis Degisken", code_13, "semantic_error")

    code_14 = """
    int x = 5;
    int x = 10;
    """
    run_test("14. Semantik: Degisken Yeniden Bildirimi", code_14, "semantic_error")

    code_15 = """
    int x = 10
    int y = 20;
    """
    run_test("15. Syntax: Eksik Noktali Virgul", code_15, "syntax_error")