import ast
import random
import string
import sys


# 解析対象のPythonコードファイル名
FILENAME = "sample.py"

def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))


class HardStringObfuscator(ast.NodeTransformer):
    def __init__(self):
        self.helper_added = False
        self.offset = random.randint(1, 10)

    def visit_Module(self, node):
        if not self.helper_added:
            helper_code = f"""
def _decode_str(data):
    return ''.join(chr(c - {self.offset}) for c in data)
"""
            helper_ast = ast.parse(helper_code).body
            node.body = helper_ast + node.body
            self.helper_added = True
        return self.generic_visit(node)

    def visit_Constant(self, node):
        # f-string内の文字列は変換しない
        if isinstance(node.value, str) and node.value:
            if isinstance(getattr(node, 'parent', None), ast.JoinedStr):
                return node
            encoded = [ord(c) + self.offset for c in node.value]
            new_node = ast.Call(
                func=ast.Name(id="_decode_str", ctx=ast.Load()),
                args=[ast.List(elts=[ast.Constant(value=v) for v in encoded], ctx=ast.Load())],
                keywords=[]
            )
            return ast.copy_location(new_node, node)
        return node

    def visit_Str(self, node):
        # f-string内の文字列は変換しない
        if node.s:
            if isinstance(getattr(node, 'parent', None), ast.JoinedStr):
                return node
            encoded = [ord(c) + self.offset for c in node.s]
            new_node = ast.Call(
                func=ast.Name(id="_decode_str", ctx=ast.Load()),
                args=[ast.List(elts=[ast.Constant(value=v) for v in encoded], ctx=ast.Load())],
                keywords=[]
            )
            return ast.copy_location(new_node, node)
        return node

    def generic_visit(self, node):
        # 子ノードに親情報を付与
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)

class NumberObfuscator(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, int) and node.value > 10:
            if random.choice([True, False]):
                # 加算式
                a = random.randint(1, node.value - 1)
                b = node.value - a
                new_node = ast.BinOp(
                    left=ast.Constant(value=a),
                    op=ast.Add(),
                    right=ast.Constant(value=b)
                )
            else:
                # XOR式
                a = random.randint(1, 1000)
                b = node.value ^ a
                new_node = ast.BinOp(
                    left=ast.Constant(value=a),
                    op=ast.BitXor(),
                    right=ast.Constant(value=b)
                )
            return ast.copy_location(new_node, node)
        return node

    def visit_Num(self, node):
        if isinstance(node.n, int) and node.n > 10:
            if random.choice([True, False]):
                # 加算式
                a = random.randint(1, node.n - 1)
                b = node.n - a
                new_node = ast.BinOp(
                    left=ast.Num(n=a),
                    op=ast.Add(),
                    right=ast.Num(n=b)
                )
            else:
                # XOR式
                a = random.randint(1, 1000)
                b = node.n ^ a
                new_node = ast.BinOp(
                    left=ast.Num(n=a),
                    op=ast.BitXor(),
                    right=ast.Num(n=b)
                )
            return ast.copy_location(new_node, node)
        return node

class ControlFlowFlattener(ast.NodeTransformer):
    def visit_If(self, node):
        if not node.orelse or not isinstance(node.parent, ast.Module):
            return self.generic_visit(node)

        state_var = generate_random_name()
        state_init = ast.Assign(
            targets=[ast.Name(id=state_var, ctx=ast.Store())],
            value=ast.Constant(value=0)
        )
        while_node = ast.While(
            test=ast.Constant(value=True),
            body=[],
            orelse=[]
        )
        if_body = node.body + [
            ast.Assign(
                targets=[ast.Name(id=state_var, ctx=ast.Store())],
                value=ast.Constant(value=1)
            )
        ]
        else_body = node.orelse + [
            ast.Assign(
                targets=[ast.Name(id=state_var, ctx=ast.Store())],
                value=ast.Constant(value=2)
            )
        ]
        flatten_if = ast.If(
            test=node.test,
            body=if_body,
            orelse=else_body
        )
        state_if1 = ast.If(
            test=ast.Compare(
                left=ast.Name(id=state_var, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value=1)]
            ),
            body=[ast.Break()],
            orelse=[]
        )
        state_if2 = ast.If(
            test=ast.Compare(
                left=ast.Name(id=state_var, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Constant(value=2)]
            ),
            body=[ast.Break()],
            orelse=[]
        )
        while_node.body = [flatten_if, state_if1, state_if2]

        return [state_init, while_node]

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)

class SingleStatementFlattener(ast.NodeTransformer):
    def visit_Expr(self, node):
        # すでにフラット化されている場合はスキップ
        if hasattr(node, '_flattened'):
            return node

        state_var = generate_random_name()
        # 状態変数初期化
        state_init = ast.Assign(
            targets=[ast.Name(id=state_var, ctx=ast.Store())],
            value=ast.Constant(value=0)
        )
        # while True:
        while_node = ast.While(
            test=ast.Constant(value=True),
            body=[
                ast.If(
                    test=ast.Compare(
                        left=ast.Name(id=state_var, ctx=ast.Load()),
                        ops=[ast.Eq()],
                        comparators=[ast.Constant(value=0)]
                    ),
                    body=[
                        node,
                        ast.Assign(
                            targets=[ast.Name(id=state_var, ctx=ast.Store())],
                            value=ast.Constant(value=1)
                        )
                    ],
                    orelse=[]
                ),
                ast.If(
                    test=ast.Compare(
                        left=ast.Name(id=state_var, ctx=ast.Load()),
                        ops=[ast.Eq()],
                        comparators=[ast.Constant(value=1)]
                    ),
                    body=[ast.Break()],
                    orelse=[]
                )
            ],
            orelse=[]
        )
        # フラット化済みフラグ
        node._flattened = True
        return [state_init, while_node]

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)

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
        # ビルトイン関数や例外だけを置き換える
        if isinstance(node.ctx, ast.Load):
            if node.id in dir(__builtins__):
                return ast.Subscript(
                    value=ast.Name(id=self.builtins_var, ctx=ast.Load()),
                    slice=ast.Constant(value=node.id),
                    ctx=ast.Load()
                )
        return node

class FunctionRenamer(ast.NodeTransformer):
    def __init__(self):
        self.rename_map = {}

    def _random_name(self, length=8):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def visit_FunctionDef(self, node):
        # 先に子ノードを処理
        self.generic_visit(node)

        # 特殊メソッドはリネームしない（__xxx__ の形式）
        if node.name.startswith("__") and node.name.endswith("__"):
            return node
        
        if node.name == "main":
            self.rename_map[node.name] = node.name
            return node
        
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

def obfuscate_python_file(file_path, output_path=None):
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # AST 解析
    tree = ast.parse(source_code)

    # Control Flow Flatteningを最初に適用
    tree = ControlFlowFlattener().visit(tree)
    ast.fix_missing_locations(tree)


    string_obfuscator = HardStringObfuscator()
    tree = string_obfuscator.visit(tree)
    ast.fix_missing_locations(tree)

    number_obfuscator = NumberObfuscator()
    tree = number_obfuscator.visit(tree)
    ast.fix_missing_locations(tree)

    tree = SingleStatementFlattener().visit(tree)
    ast.fix_missing_locations(tree)

    function_renamer = FunctionRenamer()
    tree = function_renamer.visit(tree)
    ast.fix_missing_locations(tree)


    # AST → Pythonコードへ戻す
    new_code = ast.unparse(tree)

    # 保存先
    if output_path is None:
        output_path = file_path  # 上書き
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    obfuscate_python_file(input_file, output_file)

