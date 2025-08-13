import ast
import random

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
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)