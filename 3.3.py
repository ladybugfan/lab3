def print_operation(instruction, variables):
    if instruction == "print;":
        print_all_variables(variables)
    else:
        variable_name = instruction.replace("print ", "").replace(";", "").strip()
        print_variable(variable_name, variables)
    print()

def print_variable(variable_name, variables):
    if variable_name in variables:
        if isinstance(variables[variable_name], float):
                print(f"{variable_name}: {variables[variable_name]:.2f}")
        else:
            print(f"{variable_name}: {variables[variable_name]}")
    else:
        print(f"Ошибка: переменная {variable_name} не объявлена")

def print_all_variables(variables):
    for variable_name in variables:
        if isinstance(variables[variable_name], (int, float)):
            if isinstance(variables[variable_name], float):
                print(f"{variable_name}: {variables[variable_name]:.2f}")
            else:
                print(f"{variable_name}: {variables[variable_name]}")

def interpret_instructions(data, variables = {}, scope_stack = []):

    current_function = "" 
    function_body = ""
    return_value = None

    if isinstance(data, str):
        with open(data, 'r') as file:
            lines = file.readlines()

    elif isinstance(data, list):
        lines = data
    else:
        print("Ошибка: неверный тип данных. Ожидается строка (имя файла) или массив строк.")
        return

    for instruction in lines:
        instruction = instruction.strip()
        
        if instruction.startswith("{") and current_function=="":
            scope_stack.append(variables.copy()) 
             
        elif instruction.startswith("}") and current_function=="":
            variables = scope_stack.pop()
        
        elif (instruction.startswith("}") or instruction.startswith("{")) and current_function!="":
            function_body += instruction
            if instruction=="}" and function_body.count("{")==function_body.count("}"):

                define_function(current_function+function_body, variables)
                current_function=""
                function_body = ""
                
        elif "{" in instruction and "(" in instruction:
            if instruction.endswith("}"):
                define_function(instruction, variables)
                continue
            current_function, body = list(map(str, instruction.split("{")))
            if body!="":
                function_body += body
            else:
                function_body += "{"
            
        elif instruction.endswith(";") and current_function != "":
            function_body += instruction
            
        elif instruction.endswith(";") and current_function == "":
            if instruction.startswith("print"):
                print_operation(instruction, variables)
            elif instruction.startswith("return"):
                return_value = evaluate_infix(instruction.replace("return ", "").replace(";", ""), variables)
                break
            elif ":" in instruction:
                define_function(instruction, variables)
            else:
                execute_instruction(instruction, variables)# 1
            
    variables.clear()
    scope_stack.clear()
    return return_value


def execute_instruction(instruction, variables):
    parts = instruction.split("=")
    
    if len(parts) != 1:
        
        variable_name = parts[0].strip().replace(" ", "")
        value = parts[1].strip(';').replace(" ", "")

        if variable_name in variables:
            if isinstance(variables[variable_name], int):
                variables[variable_name]=int(evaluate_infix(value, variables))
            else:
                variables[variable_name]=float(evaluate_infix(value, variables))

        elif "(" in variable_name and ")" in variable_name:
            function_name, argument = variable_name.split("(")
            argument = argument.replace(")", "").strip()

            if function_name in variables:
                print(f"Ошибка: переменная {function_name} уже объявлена")
                return
        
            if argument == "i":
                variables[function_name] = int(value)
            elif argument == "f":
                variables[function_name] = float(value)
            else:
                print(f"Ошибка: неверный аргумент для типа данных {argument}")
                return
        else:
            variables[variable_name]=evaluate_infix(value, variables) #2
    elif "(" in instruction and ")" in instruction:
        function_name, arguments = instruction.split("(")
        arguments = arguments[:-2]
        arguments = arguments.replace(" ", "").split(",")
        evaluate_function(function_name, arguments, variables)
        
    else:
        print(f"Ошибка: неверный формат инструкции {instruction}")

def define_function(instruction, variables):
    if "{" in instruction:
        function_declaration, function_body = list(map(str, instruction.split("{")))
        function_body = function_body[:-1]
    else:
        function_declaration, function_body = list(map(str, instruction.split(":")))
        function_body = function_body.replace(";", "").strip()

    if "(" in function_declaration and ")" in function_declaration:
        function_name, arguments = function_declaration.split("(")
        arguments = arguments.replace(")", "").replace(' ', '').strip().split(",")
        variables[function_name] = (arguments, function_body)
    else:
        print(f"Ошибка: неверный формат объявления функции {instruction}")
    
    variables[function_name] = (arguments, function_body)

def tokenize(expression, variables):
    tokens = []
    current_token = ''
    open_b = 0

    for char in expression:
        if char not in "-+*/()" or (char == "-" and (len(tokens)==0 or tokens[-1] in "-+*/()") and current_token == ""):
            current_token += char
        else:
            if char=='(' and current_token!='':
                current_token += char
                open_b += 1
                
            elif char==')' and open_b!=0:
                current_token += char
                open_b -= 1
                if open_b==0:
                    func_name, arg = list(map(str, current_token.split('(', 1)))
                    arg = arg[:-1].replace(" ", "")
                    current = ""
                    args = []
                    open = 0
                    
                    for i in range(len(arg)):
                        if arg[i]=="(":
                            open += 1
                            current += arg[i]
                        elif arg[i] == ")":
                            open -= 1
                            current += arg[i]
                        elif arg[i] =="," and open == 0:
                            args.append(current)
                            current = ""
                        else:
                            current += arg[i]
                        if i==len(arg)-1:
                            args.append(current)
                            
                    for i in range(len(args)):
                        args[i] = evaluate_infix(args[i], variables)    #4
                    tokens.append(evaluate_function(func_name, args, variables))  #5
                    current_token = ''
                    
            elif current_token!='' and open_b!=0:
                current_token += char
                
            elif current_token!='':
                tokens.append(current_token)
                tokens.append(char)
                current_token = ''
            else:
                tokens.append(char)
            
    if current_token:
        tokens.append(current_token)
        
    for i in range(len(tokens)):
        if tokens[i] in variables and is_number(variables[tokens[i]]):
            tokens[i] = variables[tokens[i]]
            
    return tokens

def eval_postfix(expression):
    stack = []
    operators = {'+': lambda x, y: x + y,
                 '-': lambda x, y: x - y,
                 '*': lambda x, y: x * y,
                 '/': lambda x, y: x / y}

    for token in expression.split():
        if is_number(token):
            if '.' in token:
                stack.append(float(token))
            else:
                stack.append(int(token))
        elif token in operators:
            if len(stack) < 2:
                raise ValueError("Недопустимое выражение")
            operand2 = stack.pop()
            operand1 = stack.pop()
            result = operators[token](operand1, operand2)
            stack.append(result)
        else:
            raise ValueError("Недопустимый токен: " + token)

    if len(stack) != 1:
        raise ValueError("Недопустимое выражение")

    return stack[0]

def evaluate_infix(expression, variables):
    expression = expression.replace(" ", "")
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    def higher_precedence(op1, op2):
        return precedence[op1] >= precedence[op2]

    postfix = []
    stack = []

    tokens = tokenize(expression, variables)    #3

    for token in tokens:
        if is_number(token):
            postfix.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()  
        elif token in precedence:
            while stack and stack[-1] != '(' and higher_precedence(stack[-1], token):
                postfix.append(stack.pop())
            stack.append(token)
        else:
            raise ValueError("Недопустимый токен: " + token)

    while stack:
        postfix.append(stack.pop())

    postfix_expression = ' '.join(map(str, postfix))

    result = eval_postfix(postfix_expression)   #7
    return result

def is_number(s):
    try:
        float(s) 
        return True
    except ValueError:
        return False

def evaluate_function(func_name, args, variables):
    
    if func_name in variables:
        function_definition = variables[func_name] # аргументы и тело функции из переменных
        
        if isinstance(function_definition, tuple):
            
            func_args, func_body = function_definition # из variables

            if ';' in func_body:
                func_body = [part + ';' for part in func_body.split(';') if part]
                
            else:
                for i in range(len(args)):
                    func_body = func_body.replace(func_args[i], str(args[i]))
                return evaluate_infix(func_body, variables)
            
            if len(func_args) == len(args):
                variables_copy=variables.copy()
                
                for i in range(len(func_args)):
                    try:
                        args[i] = int(args[i])
                    except ValueError:
                        try:
                            args[i] = float(args[i])
                        except ValueError:
                            pass
                    variables_copy[func_args[i]] = args[i]

                result = interpret_instructions(func_body, variables_copy)   #6
                if result is not None:
                    return result
            else:
                print(f"Ошибка: неверное количество аргументов для функции {func_name}")
        else:
            print(f"Ошибка: {func_name} не является функцией")
    else:
        print(f"Ошибка: функция {func_name} не определена")


interpret_instructions("lab3/3.txt")
