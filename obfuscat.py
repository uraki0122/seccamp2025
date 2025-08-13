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

        # 新しい名前を生成してマッピング
        new_name = self._random_name()
        self.rename_map[node.name] = new_name
        node.name = new_name
        return node

    def visit_Call(self, node):
        # 呼び出し側の名前変更（通常関数呼び出し）
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in self.rename_map:
            node.func.id = self.rename_map[node.func.id]
        return node

    def visit_Attribute(self, node):
        # 属性アクセス（メソッド呼び出し含む）を置き換える
        self.generic_visit(node)
        if node.attr in self.rename_map:
            node.attr = self.rename_map[node.attr]
        return node

class DecodeCallInliner(ast.NodeTransformer):
    def __init__(self, func_name="_decode_str"):
        self.func_name = func_name
        self.found_funcdef = None

    def visit_Module(self, node):
        # まず関数定義を探す
        for n in node.body:
            if isinstance(n, ast.FunctionDef) and n.name == self.func_name:
                self.found_funcdef = n
                break
        self.generic_visit(node)
        # 関数定義は削除する
        node.body = [n for n in node.body if not (isinstance(n, ast.FunctionDef) and n.name == self.func_name)]
        return node

    def visit_Call(self, node):
        # _decode_str(...) の呼び出しをインライン展開する
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == self.func_name:
            # 引数リストを取得
            if len(node.args) != 1:
                return node  # 引数1つ以外は変えない

            arg = node.args[0]
            if not isinstance(arg, ast.List):
                return node  # リスト以外は変えない

            # c - 1 の代わりに複雑な演算を作る関数
            def make_complex_expr(c):
                # c を受け取って chr( ((c ^ k1) - k2 + k3) ) みたいにする
                k1 = random.randint(1, 20)
                k2 = random.randint(1, 20)
                k3 = random.randint(0, 5)
                return ast.Call(
                    func=ast.Name(id='chr', ctx=ast.Load()),
                    args=[ast.BinOp(
                        left=ast.BinOp(
                            left=ast.BinOp(
                                left=ast.Name(id=c, ctx=ast.Load()),
                                op=ast.BitXor(),
                                right=ast.Constant(value=k1)
                            ),
                            op=ast.Sub(),
                            right=ast.Constant(value=k2)
                        ),
                        op=ast.Add(),
                        right=ast.Constant(value=k3))
                ],
                    keywords=[]
                )

            # リストの各要素名を固定した変数名にする（c0, c1, ...）
            element_vars = []
            elements = []
            for i, elt in enumerate(arg.elts):
                var_name = f'c{i}'
                element_vars.append(var_name)
                elements.append(ast.Assign(
                    targets=[ast.Name(id=var_name, ctx=ast.Store())],
                    value=elt
                ))

            # 各 c_i について make_complex_expr(c_i) を呼び出し
            char_exprs = [make_complex_expr(name) for name in element_vars]

            # ''.join([...]) のASTを作成
            join_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Constant(value=''),
                    attr='join',
                    ctx=ast.Load()
                ),
                args=[ast.List(elts=char_exprs, ctx=ast.Load())],
                keywords=[]
            )

            # 変数割り当て文＋joinをまとめてAST化し、置換
            # (変数宣言と ''.join(...) を1つのExprノード配列で返すため、複数文に展開可能なvisit_Callでリスト返し)
            return elements + [join_call]

        return node

class UltraMassiveObfuscator:
    def __init__(self, flatten_repeat=50, string_obf_repeat=50, dummy_repeat=150, nest_depth=20):
        self.flatten_repeat = flatten_repeat
        self.string_obf_repeat = string_obf_repeat
        self.dummy_repeat = dummy_repeat
        self.nest_depth = nest_depth

    def _generate_dummy_func(self):
        name = ''.join(random.choices(string.ascii_letters, k=12))
        arg = ''.join(random.choices(string.ascii_letters, k=5))
        var = ''.join(random.choices(string.ascii_letters, k=6))

        # 変数や定数をランダム化
        loop_limit = random.randint(5, 15)
        increment = random.choice([1, 2, 3])
        threshold = random.randint(50, 150)

        # 制御構造の種類もランダムに変えられるように（例：forループのrange, whileループの条件など）
        body_code = f"""def {name}({arg}):
        {var} = 0
        if {arg} > {random.randint(0, 5)}:
            {var} += {random.randint(1, 3)}
        else:
            {var} -= {random.randint(1, 3)}

        i = 0
        while i < {loop_limit}:
            if i % {random.choice([2,3,4])} == 0:
                {var} += i * {increment}
            else:
                {var} -= i
            i += {increment}

        for j in range({random.randint(1, loop_limit)}):
            if j == {loop_limit} // {random.choice([2,3,4])}:
                continue
            {var} += j

        while {var} < {threshold}:
            {var} += {increment}

        return {var}
    """

        return ast.parse(body_code).body[0]

    def _generate_dummy_assign(self):
        var = ''.join(random.choices(string.ascii_letters, k=8))
        val = random.randint(0, 100)
        assign = ast.Assign(
            targets=[ast.Name(id=var, ctx=ast.Store())],
            value=ast.Constant(value=val)
        )
        return assign

    def _generate_dummy_while(self, depth=5):
        var = ''.join(random.choices(string.ascii_letters, k=6))
        # 深いwhileループネストを作る
        node = ast.Pass()
        for _ in range(depth):
            node = ast.While(
                test=ast.Constant(value=True),
                body=[
                    node,
                    ast.If(
                        test=ast.Compare(
                            left=ast.Constant(value=random.randint(0, 10)),
                            ops=[ast.Eq()],
                            comparators=[ast.Constant(value=5)]
                        ),
                        body=[ast.Break()],
                        orelse=[]
                    )
                ],
                orelse=[]
            )
        return node

    def _add_nested_ifs(self, node):
        assign_count = random.randint(1, 10)
        assigns = [self._generate_dummy_assign() for _ in range(assign_count)]

        current = node
        for i in range(self.nest_depth):
            if i == self.nest_depth - random.randint(1, 10):
                body = assigns + [current]  # 無駄代入を先に挿入
            else:
                body = [current]

            current = ast.If(
                test=ast.Constant(value=True),
                body=body,
                orelse=[]
            )
        return current


    def _add_useless_assigns(self, node, count=random.randint(1, 10)):
        assigns = [self._generate_dummy_assign() for _ in range(count)]
        useless_if = ast.If(
            test=ast.Constant(value=True),  # 条件はTrueなので常に実行される
            body=assigns,
            orelse=[]
        )

        if isinstance(node, ast.Module):
            # Moduleのbodyに無駄なif文を挿入
            node.body = [useless_if] + node.body
            return node
        else:
            # それ以外はリスト化して先頭に無駄なif文を追加
            return [useless_if, node]

    def insert_useless_assign_randomly(self, node):
            if hasattr(node, 'body') and isinstance(node.body, list):
                dummy_assign = self._generate_dummy_assign()
                insert_pos = random.randint(0, len(node.body))
                node.body.insert(insert_pos, dummy_assign)



    def apply(self, tree):
        # 大量ダミー関数投入
        for _ in range(self.dummy_repeat):
            dummy = self._generate_dummy_func()
            tree.body.insert(0, dummy)

        # 文字列読化を多重にかける
        for _ in range(self.string_obf_repeat):
            string_obfuscator = HardStringObfuscator()
            tree = string_obfuscator.visit(tree)
            ast.fix_missing_locations(tree)

        # 制御フローのフラット化多重適用
        for _ in range(self.flatten_repeat):
            tree = ControlFlowFlattener().visit(tree)
            ast.fix_missing_locations(tree)
            tree = SingleStatementFlattener().visit(tree)
            ast.fix_missing_locations(tree)

        # 無駄な入れ子ifを大量に付加
        tree.body = [self._add_nested_ifs(stmt) for stmt in tree.body]

        # モジュール先頭に無駄な代入連発
        tree = self._add_useless_assigns(tree, count=100)

        ast.fix_missing_locations(tree)
        return tree

def obfuscate_python_file(file_path, output_path=None):
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # AST 解析
    tree = ast.parse(source_code)

    # Control Flow Flatteningを最初に適用
    tree = ControlFlowFlattener().visit(tree)
    ast.fix_missing_locations(tree)

    inline= DecodeCallInliner()
    tree = inline.visit(tree)
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

    over_obf = UltraMassiveObfuscator(flatten_repeat=40, string_obf_repeat=40, dummy_repeat=40)
    tree = ast.parse(source_code)
    tree = over_obf.apply(tree)

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

