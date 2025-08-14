import ast
import random
# 文字列リテラルを複数の部分文字列に分割し、使用時に ''.join([...]) で結合するように変換するクラス
class SubstringSplitter(ast.NodeTransformer):
    """
    文字列リテラルを複数の部分文字列に分割し、
    使用時に ''.join([...]) で結合するように変換するクラス
    """
    def __init__(self, max_split=5):
        self.max_split = max_split  # 最大分割数

    def visit_JoinedStr(self, node):
        # f文字列内は変更せずそのまま返す
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, str) and node.value:
            s = node.value
            num_splits = random.randint(2, min(self.max_split, len(s)))
            split_sizes = self._random_split(len(s), num_splits)
            parts = []
            index = 0
            for size in split_sizes:
                part_str = s[index:index+size]
                parts.append(ast.Constant(value=part_str))
                index += size
            # f文字列の中ではなく、普通の式として ''.join([...]) に変換
            join_call = ast.Call(
                func=ast.Attribute(value=ast.Constant(value=''), attr='join', ctx=ast.Load()),
                args=[ast.List(elts=parts, ctx=ast.Load())],
                keywords=[]
            )
            return ast.copy_location(join_call, node)
        return node

    def _random_split(self, total_length, num_splits):
        """
        total_length の文字列を num_splits 個に分割するランダムな長さのリストを作る
        """
        if num_splits >= total_length:
            return [1] * total_length
        points = sorted(random.sample(range(1, total_length), num_splits-1))
        points = [0] + points + [total_length]
        return [points[i+1] - points[i] for i in range(len(points)-1)]
