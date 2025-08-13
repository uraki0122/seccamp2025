import ast
from utils import generate_random_name

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
            ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=1))
        ]
        else_body = node.orelse + [
            ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=2))
        ]
        flatten_if = ast.If(test=node.test, body=if_body, orelse=else_body)
        state_if1 = ast.If(
            test=ast.Compare(left=ast.Name(id=state_var, ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value=1)]),
            body=[ast.Break()], orelse=[]
        )
        state_if2 = ast.If(
            test=ast.Compare(left=ast.Name(id=state_var, ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value=2)]),
            body=[ast.Break()], orelse=[]
        )
        while_node.body = [flatten_if, state_if1, state_if2]

        return [state_init, while_node]

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)