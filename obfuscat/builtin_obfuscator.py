import ast
from utils import generate_random_name
# 組み込み関数を難読化するためのクラス（特殊メソッドは難読化の対象外なため__builtins__を使用）
class BuiltinObfuscator(ast.NodeTransformer):
    def __init__(self):
        self.builtins_var = generate_random_name()
        self.helper_inserted = False

    def visit_Module(self, node):
        if not self.helper_inserted:
            assign_builtin = ast.Assign(
                targets=[ast.Name(id=self.builtins_var, ctx=ast.Store())],
                value=ast.Name(id="__builtins__", ctx=ast.Load())
            )
            node.body.insert(0, assign_builtin)
            self.helper_inserted = True
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id in dir(__builtins__):
                return ast.Subscript(
                    value=ast.Name(id=self.builtins_var, ctx=ast.Load()),
                    slice=ast.Constant(value=node.id),
                    ctx=ast.Load()
                )
        return node