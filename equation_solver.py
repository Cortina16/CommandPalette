import sys

import sympy
from sympy.parsing import sympy_parser as sym_parse
import ast

# def solve(expression):
#     try:
#         expression = sympy.sympify(expression)
#     except Exception:
#         return ""

def get_first_var(eq):
    if type(eq) == tuple:
        eq = eq[1]
    print(eq)
    variables = eq.free_symbols
    if not variables:
        return eq
    return list(variables)[0]
def generate_expression(str, *args):
    try:
        vars = [x for x in sympy.symbols(args)]
    except Exception:
        pass
    sides = str.split("=")
    transformations=(sym_parse.standard_transformations + (sym_parse.implicit_multiplication_application,))
    lhs_str = sides[0].strip()
    rhs_str = sides[1].strip()
    lhs_expr = sympy.parse_expr(lhs_str, transformations=transformations)
    rhs_expr = sympy.parse_expr(rhs_str, transformations=transformations)
    return sympy.Eq(lhs_expr, rhs_expr)



def next_step(expression: sympy.Equality):
    current_eq = expression

    msg, next_eq = isolate(current_eq)
    if msg: return [(msg, next_eq)]

    msg, next_eq = power_cleanup(current_eq)
    if msg: return [(msg, next_eq)]

    msg, next_eq = zero_prod_prop(current_eq)
    if msg: return [(msg, next_eq)]

    msg, next_eq = sqrt(current_eq)
    if msg: return [(msg, next_eq)]


    if not is_linear(current_eq.lhs):
        msg, next_eq = factoring(current_eq)
        if msg: return [(msg, next_eq)]
        msg, next_eq = distribute(current_eq)
        if msg: return [(msg, next_eq)]
    msg, next_eq = coefficient_cleanup(current_eq)
    if msg: return [(msg, next_eq)]
    return []


def solve_recursive(task):
    eq = task["eq"]
    history = task["history"]

    steps = next_step(eq)

    if not steps:
        return history

    msg, result = steps[0]
    # result = next_step(eq)

    if isinstance(result, list):
        branch_result = []
        for i, branch in enumerate(result):
            new_task = {
                "eq": branch,
                "history" : history + [(f"{msg} Factor {i+1}", branch)]
            }
            branch_result.append(solve_recursive(new_task))
        return branch_result
    new_task = {
        "eq" : result,
        "history" : history + [(msg, result)]
    }
    return solve_recursive(new_task)



        # if lhs.is

def coefficient_cleanup(eq):
    lhs, rhs = eq.lhs, eq.rhs
    coefficient = lhs.coeff(get_first_var(eq))
    if coefficient != 1 and coefficient != 0:
        new_eq = sympy.Eq(lhs / coefficient, rhs / coefficient)
        return f"Divide both sides by {coefficient}", new_eq
    return None, eq

def isolate(eq):
    lhs, rhs = eq.lhs, eq.rhs

    var = get_first_var(eq)

    poly = sympy.Poly(lhs, var)
    coeffs = poly.all_coeffs()
    is_pure_quadratic = (len(coeffs) == 3 and coeffs[1] == 0)
    if sympy.degree(eq.lhs, gen=var) > 1 and not is_pure_quadratic:
        return None, eq
    constant, x_terms = lhs.as_independent(var, as_Add=True)
    new_eqn = sympy.Eq(lhs-constant, rhs-constant)
    if eq != new_eqn:
        return f"Isolate {var}", new_eqn
    return None, eq


def distribute(eq):
    lhs, rhs = eq.lhs, eq.rhs
    var = get_first_var(eq)
    new_lhs = sympy.expand(eq.lhs)
    new_rhs = sympy.expand(eq.rhs)
    if new_lhs != eq.lhs or new_rhs != eq.rhs:
        return "Distribute terms", sympy.Eq(new_lhs, new_rhs)
    return None, eq

def combine_like_terms(eq):
    lhs, rhs = eq.lhs, eq.rhs
    var = get_first_var(eq)
    lhs = sympy.collect(lhs, var)
    rhs = sympy.collect(rhs, var)
    eqn = sympy.Eq(lhs, rhs)
    return f"combine like terms", eqn
    pass

def power_cleanup(eq):
    lhs, rhs = eq.lhs, eq.rhs
    if rhs == 0 and isinstance(lhs, sympy.Pow):
        base = lhs.base
        return f"Take the square root of both sides", sympy.Eq(base,rhs)
    return None, eq

def sqrt(eq):
    lhs, rhs = eq.lhs, eq.rhs
    var = get_first_var(eq)
    if isinstance(lhs, sympy.Pow) and lhs.exp == 2:
        res = sympy.sqrt(rhs)
        return "Take the square root of both sides", [sympy.Eq(lhs.base, res), sympy.Eq(lhs.base, -res)]
    return None, eq
#polynomials

def expand_conjugates(eq):
    lhs, rhs = eq.lhs, eq.rhs
    var = get_first_var(eq)
    new_lhs = sympy.expand(lhs, multinomial=True)
    new_rhs = sympy.expand(rhs, multinomial=True)
    eqn = sympy.Eq(lhs, rhs)
    if new_lhs != eq.lhs or new_rhs != eq.rhs:
        return "Expand Terms", sympy.Eq(new_lhs, new_rhs)
    return None, eq

def factoring(eq):
    lhs, rhs = eq.lhs, eq.rhs
    if eq.rhs != 0:
        return None, eq
    var = get_first_var(eq)
    new_lhs = sympy.factor(lhs)
    new_rhs = sympy.factor(rhs)
    eqn = sympy.Eq(lhs, rhs)
    if new_lhs != eq.lhs or new_rhs != eq.rhs:
        return "Factor terms", sympy.Eq(new_lhs, new_rhs)
    return None, eq

def zero_prod_prop(eq):
    lhs, rhs = eq.lhs, eq.rhs
    if rhs == 0 and isinstance(lhs, sympy.Mul):
        factors = lhs.args
        new_equations=[sympy.Eq(f,0) for f in factors if f.has(get_first_var(eq))]
        return "Apply zero product property", new_equations
    return None, eq
#facor big boys
def rational_root_theorem(eq):
    pass

#logs/exponentials
#log(a)+log(b)=log(ab)
def product_quotient(eq):
    pass

#log(x^n) == nlog(x)
def power_rule(eq):
    pass
#log_b(x)=(log_k(x))/(log_k(b))
def change_of_base(eq):
    pass
#exponent bases = a^x*a^y= a^(x+y)


#backend help (for our use only)
def is_linear(eq):
    var = get_first_var(eq)
    return sympy.degree(eq, gen=var) <= 1

def formatter(steps):
    str = ""

    def str_builder(steps, level=0):
        nonlocal str
        indent = "  " * level

        if isinstance(steps, tuple):
            msg, eq = steps
            str += (f"{indent}↳ {msg}: {eq}\n")
            return

        if isinstance(steps, list):
            for step in steps:
                if isinstance(step, list) and len(step) > 0 and isinstance(step[0], list):
                    str += (f"{indent} Split into {len(step)} cases:\n")
                    for i, branch in enumerate(step):
                        str += (f"{indent} Case {i + 1}:\n")
                        str_builder(branch, level + 2)
                else:
                    str_builder(step, level)
    str_builder(steps)
    return str


eqn = generate_expression("9x**2+12x+4=0")
print(next_step(eqn))
eqn = generate_expression("x**3-x**2+4x-4=0")
tree = solve_recursive({"eq":eqn,"history": [("Start", eqn)]})

def solve_eqn(eqn):
    eqn = generate_expression(eqn)
    tree = solve_recursive({"eq":eqn,"history": [("Start", eqn)]})
    return formatter(tree)

# print(""
#       "")
# for item in tree:
#     for sub_item in item:
#         print(sub_item)
#         if type(sub_item) == list:
#             print("")
#             for sub_sub_item in sub_item:
#                 print(sub_sub_item)

wrapper = {

}
print("\n\n")
print(formatter(tree))

