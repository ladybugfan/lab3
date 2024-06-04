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


def interpret_instructions(file_name):
    variables = {}
    with open(file_name, 'r') as file:
        
        for line in file:
            instruction = line.strip()
            if instruction.endswith(";"):
                if ":" in instruction:
                    define_function(instruction, variables)
                elif instruction.startswith("print"):
                    print_operation(instruction, variables)
                else:
                    execute_instruction(instruction, variables)
    variables.clear()


def execute_instruction(instruction, variables):
    parts = instruction.split("=")
    
    if len(parts[0]) != 0 and len(parts[1]) != 0:
        
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
            variables[variable_name]=evaluate_infix(value, variables)
    else:
        print(f"Ошибка: неверный формат инструкции {instruction}")


def define_function(instruction, variables):
    parts = instruction.split(":")
    function_declaration = parts[0].strip()
    function_body = parts[1].replace(";", "").strip()

    if "(" in function_declaration and ")" in function_declaration:
        function_name, arguments = function_declaration.split("(")
        arguments = arguments.replace(")", "").replace(' ', '').strip()
        variables[function_name] = (arguments, function_body)
    else:
        print(f"Ошибка: неверный формат объявления функции {instruction}")

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
        if isinstance(variables[func_name], tuple):
            func_args, func_body = variables[func_name]
            if len(func_args.split(',')) == len(args):
                func_body_with_args = func_body
                for i in range(len(args)):
                    func_body_with_args = func_body_with_args.replace(func_args.split(',')[i], str(args[i]))
                return evaluate_infix(func_body_with_args, variables)
            else:
                print(f"Ошибка: неверное количество аргументов для функции {func_name}")
        else:
            print(f"Ошибка: {func_name} не является функцией")
    else:
        print(f"Ошибка: функция {func_name} не определена")
        


interpret_instructions("lab3/2.txt")