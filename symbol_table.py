class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
    
    def enter_scope(self):
        self.scopes.append({})
    
    def exit_scope(self):
        self.scopes.pop()
    
    def add_symbol(self, name, info):
        self.scopes[-1][name] = info
    
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def check_current_scope(self, name):
        return name in self.scopes[-1]

    # Debuglamak icin scope'u yazdirma
    def print_current_scope(self, scope_name="Scope"):
        """En ustteki (topmost) scope'u yazdirir."""
        depth = len(self.scopes) - 1
        indent = "    " * depth
        print(f"{indent}--- {scope_name} (Derinlik: {depth}) ---")
        if not self.scopes[-1]:
            print(f"{indent}(Bos)")
        else:
            for name, info in self.scopes[-1].items():
                print(f"{indent}  {name}: {info}")
        print(f"{indent}------------------------------")