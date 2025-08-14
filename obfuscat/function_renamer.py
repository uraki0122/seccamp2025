import ast
import random
import string
# 関数名をランダムに変更するためのクラス
class FunctionRenamer(ast.NodeTransformer):
    def __init__(self):
        self.rename_map = {}

    def _random_name(self, length=8):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if node.name.startswith("__") and node.name.endswith("__"):
            return node
        new_name = self._random_name()
        self.rename_map[node.name] = new_name
        node.name = new_name
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in self.rename_map:
            node.func.id = self.rename_map[node.func.id]
        return node

    def visit_Attribute(self, node):
        self.generic_visit(node)
        if node.attr in self.rename_map:
            node.attr = self.rename_map[node.attr]
        return node