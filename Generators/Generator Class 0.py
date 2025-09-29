import random
import numpy as np
from deap import base, creator, tools, algorithms

# Função que cria um código Python aleatório como string
def generate_python_code():
    libraries = ['math', 'random', 'numpy', 'time', 'collections', 'itertools', 'sys', 'os', 'functools']
    imports = random.sample(libraries, random.randint(1, len(libraries)))
    functions = []
    for _ in range(random.randint(2, 10)):
        func_name = f"func_{random.randint(0, 1000)}"
        num_operations = random.randint(4, 20)
        ops = []
        local_vars = set()
        for _ in range(num_operations):
            operation_type = random.choice(['assignment', 'conditional', 'loop', 'function_call'])
            var_name = f"var_{random.randint(0, 100)}"
            if var_name not in local_vars:
                ops.append(f"{var_name} = 0")
                local_vars.add(var_name)
            else:
                ops.append(f"{var_name} = {var_name} + {random.randint(1, 50)}")

            if operation_type == 'assignment':
                ops.append(f"{var_name} = {var_name} + {random.randint(1, 50)}")
                
            elif operation_type == 'conditional':
                ops.append(f"if {var_name} > {random.randint(1, 50)}:\n        {var_name} = {var_name} * {random.randint(1, 50)}")
            
            elif operation_type == 'loop':
                loop_var = f"i_{random.randint(0, 100)}"
                dependent_var = random.choice(list(local_vars))
                
                # Certifique-se de que dependent_var está declarada e inicializada
                if dependent_var not in local_vars:
                    ops.append(f"{dependent_var} = {random.randint(1, 10000)}")
                    local_vars.add(dependent_var)
                    
                    
                ops.append(f"{loop_var} = 0")
                ops.append(f"for {loop_var} in range({dependent_var}):\n        {dependent_var} += {loop_var}")
           
            elif operation_type == 'function_call':
                ops.append(f"print('Debug:', {var_name})")
        body = '\n    '.join(ops)
        return_statement = f"return {var_name}" if local_vars else "return None"
        functions.append(f"def {func_name}():\n    {body}\n    {return_statement}")
    
    imports_code = '\n'.join([f"import {lib}" for lib in imports])
    functions_code = '\n\n'.join(functions)
    code = f"{imports_code}\n\n{functions_code}"
    
    return code

# Função de fitness que avalia o código gerado
def fitness(individual):
    code = individual[0]
    score = 0
    num_imports = code.count('import ')
    if 1 <= num_imports <= 12:
        score += 1
    else:
        score -= 1
    num_funcs = code.count('def ')
    if 2 <= num_funcs <= 8:
        score += 1
    else:
        score -= 1
    num_ifs = code.count('if ')
    if 2 <= num_ifs <= 8:
        score += 1
    else:
        score -= 1
    num_prints = code.count('print')
    if 2 <= num_prints <= 8:
        score += 1
    else:
        score -= 1
    num_vars = code.count('var_')
    if 2 <= num_vars <= 100:
        score += 1
    else:
        score -= 1
    num_fors = code.count('for ')
    if 1 <= num_fors <= 6:
        score += 1
    else:
        score -= 5 
    num_lines = len(code.split('\n'))
    if 10 <= num_lines <= 150:
        score += 1
    else:
        score -= 1
    try:
        compiled_code = compile(code, '<string>', 'exec')
        exec(compiled_code)
        score += 1
    except Exception as e:
        score -= 5
    return score,

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_code", generate_python_code)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_code, n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def cxCrossover(ind1, ind2):
    code1 = ind1[0].split('\n')
    code2 = ind2[0].split('\n')
    crossover_point = random.randint(1, min(len(code1), len(code2)) - 1)
    new_code1 = code1[:crossover_point] + code2[crossover_point:]
    new_code2 = code2[:crossover_point] + code1[crossover_point:]
    ind1[0] = '\n'.join(new_code1)
    ind2[0] = '\n'.join(new_code2)
    return ind1, ind2

def mutSmallChange(ind):
    code_lines = ind[0].split('\n')
    mutation_type = random.choice(['modify_variable', 'change_operation', 'add_print'])
    if mutation_type == 'modify_variable':
        candidates = [i for i, line in enumerate(code_lines) if '=' in line and 'for ' not in line]
        if candidates:
            line_idx = random.choice(candidates)
            var_assignment = code_lines[line_idx].split('=')
            new_value = random.randint(1, 50)
            code_lines[line_idx] = f"{var_assignment[0].strip()} = {new_value}"
    elif mutation_type == 'change_operation':
        candidates = [i for i, line in enumerate(code_lines) if '+=' in line or '*=' in line]
        if candidates:
            line_idx = random.choice(candidates)
            if '+=' in code_lines[line_idx]:
                code_lines[line_idx] = code_lines[line_idx].replace('+=', '*=')
            elif '*=' in code_lines[line_idx]:
                code_lines[line_idx] = code_lines[line_idx].replace('*=', '+=')
    elif mutation_type == 'add_print':
        var_candidates = [line.split()[0] for line in code_lines if '=' in line and 'for ' not in line]
        if var_candidates:
            var_to_print = random.choice(var_candidates)
            insert_position = random.randint(0, len(code_lines) - 1)
            code_lines.insert(insert_position, f"print('Debug:', {var_to_print})")
    ind[0] = '\n'.join(code_lines)
    return ind,

toolbox.register("mate", cxCrossover)
toolbox.register("mutate", mutSmallChange)
toolbox.register("select", tools.selRoulette)
toolbox.register("evaluate", fitness)

def main():
    pop = toolbox.population(n=10000)
    hof = tools.HallOfFame(500)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)
    
    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.9, mutpb=0.1, ngen=50, stats=stats, halloffame=hof, verbose=True)
    
    print("Codes:")
    for i, ind in enumerate(hof):
        print(f"Code {i + 1}:\n{ind[0]}\n\n{'='*40}\n")
    
    with open("codes_dependentes.py", "w") as file:
        for i, ind in enumerate(hof):
            file.write(f"Code {i + 1}:\n{ind[0]}\n\n{'='*40}\n")

if __name__ == "__main__":
    main()
