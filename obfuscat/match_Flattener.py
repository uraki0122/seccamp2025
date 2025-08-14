import ast
import random
# ASTのif文をmatch文に変換するためのクラス
class MatchFlattener(ast.NodeTransformer):
    def __init__(self, max_depth=5):
        self.max_depth = max_depth

    def visit_If(self, node, current_depth=0):
        self.generic_visit(node)
        
        # ネストが深すぎたらフラット化しない
        if current_depth >= self.max_depth:
            return node

        # ランダムに match に変換するか判定
        if random.choice([True, False]):
            # match 文に変換
            match_node = ast.Match(
                subject=ast.Constant(value=True),
                cases=[
                    ast.match_case(
                        pattern=ast.MatchValue(ast.Constant(value=True)),
                        body=node.body
                    ),
                    ast.match_case(
                        pattern=ast.MatchValue(ast.Constant(value=False)),
                        body=node.orelse or [ast.Pass()]
                    )
                ]
            )
            return match_node
        else:
            # 元の if を残す
            return node

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().generic_visit(node)
