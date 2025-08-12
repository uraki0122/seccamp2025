import ast
import random
import string

class FunctionRenamer(ast.NodeTransformer):
    def __init__(self):
        self.rename_map = {}

    def _random_name(self, length=8):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def visit_FunctionDef(self, node):
        # 子ノードを先に処理
        self.generic_visit(node)

        # 新しい名前を生成してマッピング
        new_name = self._random_name()
        self.rename_map[node.name] = new_name
        node.name = new_name
        return node

    def visit_Call(self, node):
        # 呼び出し側の名前変更
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in self.rename_map:
            node.func.id = self.rename_map[node.func.id]
        return node

def obfuscate_function_names(source_code):
    tree = ast.parse(source_code)
    renamer = FunctionRenamer()
    tree = renamer.visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

if __name__ == "__main__":
    with open("sample.py", "r", encoding="utf-8") as f:
        source = f.read()

    obfuscated = obfuscate_function_names(source)
    with open("obfuscated.py", "w", encoding="utf-8") as f:
        f.write(obfuscated)
