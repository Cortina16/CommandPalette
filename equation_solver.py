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
    if isinstance(expression, sympy.Equality):
        lhs = expression.lhs
        rhs = expression.rhs

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
    constant, x_terms = lhs.as_independent(var)
    eqn = sympy.Eq(lhs-constant, rhs-constant)
    return f"Isolate {var}", eqn

eqn = generate_expression("3x-1=2")
step, eq = isolate(eqn)
step2, eq2 = coefficient_cleanup(eq)
print(f"{step}, {step2}, {eq2}")

# print(coefficient_cleanup(isolate(generate_expression("3x-1=2"))))

