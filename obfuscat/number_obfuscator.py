import ast
import random

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
    