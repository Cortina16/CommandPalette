import ast
import math
import operator
import re
from decimal import Decimal

operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.LShift: operator.lshift,
    ast.RShift: operator.rshift,
    ast.USub: operator.neg,
}
constants = {
    "pi" : Decimal(str(math.pi)),
    "e" : Decimal(str(math.e))
}

def evaluate_ast(node):
    try:
        if isinstance(node, ast.Constant):
            return Decimal(str(node.value))
        elif isinstance(node, ast.Name):
            if node.id.lower() in constants:
                return constants[node.id.lower()]
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](evaluate_ast(node.left), evaluate_ast(node.right))
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](evaluate_ast(node.operand))
        else:
            pass
    except Exception:
        pass

def calculate(expression):
    try:
        expression = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', expression)
        tree = ast.parse(expression.replace("^", "**"), mode="eval")
        return evaluate_ast(tree.body)
    except:
        return ""

print(calculate("3^2"))