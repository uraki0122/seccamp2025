import ast
import random

# デコード関数の呼び出しをインライン化するためのクラスです
class DecodeCallInliner(ast.NodeTransformer):
    def __init__(self, func_name="_decode_str"):
        self.func_name = func_name
        self.found_funcdef = None

    def visit_Module(self, node):
        for n in node.body:
            if isinstance(n, ast.FunctionDef) and n.name == self.func_name:
                self.found_funcdef = n
                break
        self.generic_visit(node)
        node.body = [n for n in node.body if not (isinstance(n, ast.FunctionDef) and n.name == self.func_name)]
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == self.func_name:
            if len(node.args) != 1 or not isinstance(node.args[0], ast.List):
                return node

            arg = node.args[0]
            def make_complex_expr(c):
                k1 = random.randint(1, 20)
                k2 = random.randint(1, 20)
                k3 = random.randint(0, 5)
                return ast.Call(
                    func=ast.Name(id='chr', ctx=ast.Load()),
                    args=[ast.BinOp(
                        left=ast.BinOp(
                            left=ast.BinOp(left=ast.Name(id=c, ctx=ast.Load()), op=ast.BitXor(), right=ast.Constant(value=k1)),
                            op=ast.Sub(), right=ast.Constant(value=k2)
                        ),
                        op=ast.Add(), right=ast.Constant(value=k3))
                    ],
                    keywords=[]
                )

            element_vars = [f'c{i}' for i in range(len(arg.elts))]
            elements = [ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=elt) for i, (var_name, elt) in enumerate(zip(element_vars, arg.elts))]
            char_exprs = [make_complex_expr(name) for name in element_vars]
            join_call = ast.Call(
                func=ast.Attribute(value=ast.Constant(value=''), attr='join', ctx=ast.Load()),
                args=[ast.List(elts=char_exprs, ctx=ast.Load())],
                keywords=[]
            )
            return elements + [join_call]

        return node