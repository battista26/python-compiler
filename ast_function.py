def print_ast(node, indent=""):
    # AST ağacını okunabilir yazdırma
    if isinstance(node, list):
        for item in node:
            print_ast(item, indent)
    elif hasattr(node, "__dict__"):
        print(f"{indent}{node.__class__.__name__}")

        for key, value in vars(node).items():
            if isinstance(value, list):
                if value:
                    print(f"{indent}  {key}: [")
                    
                    for item in value:
                        print_ast(item, indent + "    ")

                    print(f"{indent}  ]")
                else:
                    print(f"{indent}  {key}: []")
            elif hasattr(value, "__dict__"):
                print(f"{indent}  {key}:")
                print_ast(value, indent + "    ")
            elif value is None:
                print(f"{indent}  {key}: None")
            else:
                print(f"{indent}  {key}: {value}")
    else:
        # Primitives
        print(f"{indent}{node}")