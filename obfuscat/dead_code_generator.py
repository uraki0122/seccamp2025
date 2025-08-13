import ast
import random

class DeadCodeGenerator:
    def __init__(self, available_vars):
        self.available_vars = available_vars if available_vars else ['x'] # Fallback

    def random_true_condition(self):
        var = random.choice(self.available_vars)
        patterns = [
            lambda v: ast.Compare(left=ast.Name(id=v, ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Name(id=v, ctx=ast.Load())]),
            lambda v: ast.Compare(left=ast.Constant(value=5), ops=[ast.Lt()], comparators=[ast.Constant(value=10)]),
            lambda v: ast.Compare(left=ast.Constant(value=100), ops=[ast.Gt()], comparators=[ast.Constant(value=10)]),
            lambda v: ast.BoolOp(op=ast.Or(), values=[ast.Constant(value=True), ast.Constant(value=False)]),
            lambda v: ast.UnaryOp(op=ast.Not(), operand=ast.Constant(value=False)),
            lambda v: ast.Compare(left=ast.Constant(value="x"), ops=[ast.NotEq()], comparators=[ast.Constant(value="y")]),
            lambda v: ast.Compare(left=ast.BinOp(left=ast.Constant(value=1), op=ast.BitOr(), right=ast.Constant(value=2)),
                                  ops=[ast.Gt()], comparators=[ast.Constant(value=0)])
        ]
        # Handle case where var might not be defined.
        try:
            return random.choice(patterns)(var)
        except NameError:
             return ast.Constant(value=True)