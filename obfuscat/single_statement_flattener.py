import ast
from utils import generate_random_name
# 単一のステートメントをフラット化するためのクラス
class SingleStatementFlattener(ast.NodeTransformer):
    def visit_Expr(self, node):
        if hasattr(node, '_flattened'):
            return node

        state_var = generate_random_name()
        state_init = ast.Assign(
            targets=[ast.Name(id=state_var, ctx=ast.Store())],
            value=ast.Constant(value=0)
        )
        while_node = ast.While(
            test=ast.Constant(value=True),
            body=[
                ast.If(
                    test=ast.Compare(left=ast.Name(id=state_var, ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value=0)]),
                    body=[node, ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=1))],
                    orelse=[]
                ),
                ast.If(
                    test=ast.Compare(left=ast.Name(id=state_var, ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value=1)]),
                    body=[ast.Break()],
                    orelse=[]
                )
            ],
            orelse=[]
        )
        node._flattened = True
        return [state_init, while_node]

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)