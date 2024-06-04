


def parse_instructions(file_paths):
    variables = {}  
    scope_stack = [] 

    def show_variables():
        print("ShowVar:")
        for var, val in variables.items():
            print(f"{var}={val}")
        print()

    for file_path in file_paths:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line == '':
                    break
                
                if line.startswith("{"):
                    scope_stack.append(variables.copy())  
                elif line.startswith("}"):
                    variables = scope_stack.pop()  
                elif line.startswith("ShowVar"):
                    show_variables()
                else:
                    parts = line.split("=")
                    var_name = parts[0].strip()
                    var_value = parts[1].strip().rstrip(';') 
                    variables[var_name] = var_value


file_paths = ["lab3/1.txt"]
parse_instructions(file_paths)

