import ast
import random
import marshal


class CompiledStringObfuscator(ast.NodeTransformer):
    """
    _decode_str をコンパイルして marshal に埋め込み、実行時に types.FunctionType で復元する。
    """
    def __init__(self, offset=None):
        self.helper_added = False
        self.offset = offset if offset is not None else random.randint(1, 10)

    def visit_Module(self, node):
        if not self.helper_added:
            # 元の関数コードを作る
            code_obj = compile(
                f"def _decode_str(data):\n"
                f"    return ''.join(chr(c - {self.offset}) for c in data)\n",
                "<string>",
                "exec"
            )
            # marshal によるバイト化
            for n in code_obj.co_consts:
                if isinstance(n, type(code_obj)):
                    func_code_bytes = marshal.dumps(n)
                    break
            else:
                raise RuntimeError("Code object not found")

            # AST に埋め込み
            helper_code = f"""
import marshal
import types
_decode_str = types.FunctionType(marshal.loads({func_code_bytes}), globals())
"""
            helper_ast = ast.parse(helper_code).body
            node.body = helper_ast + node.body
            self.helper_added = True

        return self.generic_visit(node)

    def visit_Constant(self, node):
        # 文字列定数を変換
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

    def generic_visit(self, node):
        # 子ノードに親情報を付与
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)
