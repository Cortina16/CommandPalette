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
    steps = []
    stack = [expression]
    current_eq = expression
    var = get_first_var(current_eq)
    runs = 0
    expanded = False

    print(current_eq.rhs.is_constant())
    print(current_eq.lhs == var)
    print(current_eq.lhs == var and current_eq.rhs.is_constant())

    while not (current_eq.lhs == var and current_eq.rhs.is_constant()):
        print(f" run: {runs}", end='\r', flush=True)
        sys.stdout.write(f'\r{runs}')
        sys.stdout.flush()
        print(current_eq)
        if expanded == False:
            msg, next_eq = distribute(current_eq)
            if msg:
                steps.append((msg, next_eq))
                current_eq = next_eq
                print('distributed')
                continue
            expanded = True
        if not is_linear(current_eq):
            msg, next_eq = factoring(current_eq)
            if msg:
                steps.append((msg, next_eq))
                current_eq = next_eq
                print('factoring')
                continue
        msg, next_eq = power_cleanup(current_eq)
        if msg:
            steps.append((msg, next_eq))
            current_eq = next_eq
            print('power_cleanuping')
            continue

        msg, next_eq = zero_prod_prop(current_eq)
        if msg:
            steps.append((msg, next_eq))
            current_eq = next_eq
            print('zero prod')
            continue
        msg, next_eq = isolate(current_eq)
        if msg:
            steps.append((msg, next_eq))
            current_eq = next_eq
            print('isolate')
            continue
        msg, next_eq = coefficient_cleanup(next_eq)
        if msg:
            steps.append((msg, next_eq))
            current_eq = next_eq
            print('cleaning')
            continue
        runs += 1
        break

    return steps





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

eqn = generate_expression("9x**2+12x+4=0")
print(next_step(eqn))
eqn = generate_expression("x**3-x**2+4x-4=0")
print(next_step(eqn))

# step, eq = isolate(eqn)
# step2, eq2 = coefficient_cleanup(eq)
# print(f"{step}, {step2}, {eq2}")

# print(coefficient_cleanup(isolate(generate_expression("3x-1=2"))))

