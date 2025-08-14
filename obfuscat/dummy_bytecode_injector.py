import ast
import random

class DummyBytecodeInjector:
    def __init__(self):
        self.dummy_payloads = [
            "sum([i*i for i in range(1000)])",
            "''.join(chr((ord(c)+1)%256) for c in 'junk')",
            "import math; math.sqrt(12345)",
            "list(map(lambda x: x**3, range(50)))",
            "b''.join(bytes([x ^ 0x42]) for x in b'random')"
        ]

    def make_dummy_code(self):
        code_str = random.choice(self.dummy_payloads)
        return ast.Expr(value=ast.Call(
            func=ast.Name(id="exec", ctx=ast.Load()),
            args=[ast.Constant(value=code_str)],
            keywords=[]
        ))

    def inject_into_tree(self, tree):
        # if True ブロックに元のコードを入れ、else にダミーを入れる
        new_body = []
        for node in tree.body:
            if_stmt = ast.If(
                test=ast.Constant(value=True),
                body=[node],
                orelse=[self.make_dummy_code()]
            )
            new_body.append(if_stmt)
        tree.body = new_body
        return tree
