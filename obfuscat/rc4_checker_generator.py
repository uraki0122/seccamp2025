
import ast
import random
import string

def random_name(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

class RC4CheckGenerator(ast.NodeTransformer):
    """
    RC4鍵チェック関数を生成・難読化する。
    関数を AST で作成するので、既存の obfuscator に組み込める
    """
    def __init__(self, key_bytes: bytes, check_data: bytes, target_bytes: bytes):
        self.key_bytes = key_bytes
        self.check_data = check_data
        self.target_bytes = target_bytes

        # 関数名もランダムに
        self.func_name = random_name()
        self.s_table_var = random_name()
        self.i_var = random_name()
        self.j_var = random_name()
        self.out_var = random_name()
        self.k_var = random_name()
        self.key_var = random_name()
        self.data_var = random_name()
        self.target_var = random_name()

    def _bytes_to_ast_list(self, b: bytes):
        # バイト列を ast.List に変換
        return ast.List(elts=[ast.Constant(value=v) for v in b], ctx=ast.Load())

    def generate(self) -> ast.FunctionDef:
        """RC4チェック関数の AST を生成"""
        # Sテーブル初期化
        s_init = ast.Assign(
            targets=[ast.Name(id=self.s_table_var, ctx=ast.Store())],
            value=ast.List(elts=[ast.Constant(value=i) for i in range(256)], ctx=ast.Load())
        )

        # key と data と target を分割変数として格納
        key_assign = ast.Assign(
            targets=[ast.Name(id=self.key_var, ctx=ast.Store())],
            value=self._bytes_to_ast_list(self.key_bytes)
        )
        data_assign = ast.Assign(
            targets=[ast.Name(id=self.data_var, ctx=ast.Store())],
            value=self._bytes_to_ast_list(self.check_data)
        )
        target_assign = ast.Assign(
            targets=[ast.Name(id=self.target_var, ctx=ast.Store())],
            value=self._bytes_to_ast_list(self.target_bytes)
        )

        # ksa ループ
        ksa_loop = ast.For(
            target=ast.Name(id=self.i_var, ctx=ast.Store()),
            iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(value=256)], keywords=[]),
            body=[
                ast.Assign(
                    targets=[ast.Name(id=self.j_var, ctx=ast.Store())],
                    value=ast.BinOp(
                        left=ast.BinOp(
                            left=ast.Name(id=self.j_var, ctx=ast.Load()) if hasattr(self, 'j_var') else ast.Constant(value=0),
                            op=ast.Add(),
                            right=ast.Subscript(
                                value=ast.Name(id=self.s_table_var, ctx=ast.Load()),
                                slice=ast.Name(id=self.i_var, ctx=ast.Load()),
                                ctx=ast.Load()
                            )
                        ),
                        op=ast.Add(),
                        right=ast.Subscript(
                            value=ast.Name(id=self.key_var, ctx=ast.Load()),
                            slice=ast.BinOp(left=ast.Name(id=self.i_var, ctx=ast.Load()), op=ast.Mod(), right=ast.Call(func=ast.Name(id='len', ctx=ast.Load()), args=[ast.Name(id=self.key_var, ctx=ast.Load())], keywords=[])),
                            ctx=ast.Load()
                        )
                    )
                ),
                ast.Assign(
                    targets=[ast.Tuple(elts=[ast.Name(id=self.s_table_var, ctx=ast.Store()), ast.Name(id=self.s_table_var, ctx=ast.Store())], ctx=ast.Store())],
                    value=ast.Tuple(
                        elts=[
                            ast.Subscript(value=ast.Name(id=self.s_table_var, ctx=ast.Load()), slice=ast.Name(id=self.i_var, ctx=ast.Load()), ctx=ast.Load()),
                            ast.Subscript(value=ast.Name(id=self.s_table_var, ctx=ast.Load()), slice=ast.Name(id=self.j_var, ctx=ast.Load()), ctx=ast.Load())
                        ],
                        ctx=ast.Load()
                    )
                )
            ],
            orelse=[]
        )

        # 暗号化ループ（enc）
        enc_loop = ast.Assign(
            targets=[ast.Name(id=self.out_var, ctx=ast.Store())],
            value=ast.List(elts=[], ctx=ast.Load())
        )

        i_assign = ast.Assign(targets=[ast.Name(id=self.i_var, ctx=ast.Store())], value=ast.Constant(value=0))
        j_assign = ast.Assign(targets=[ast.Name(id=self.j_var, ctx=ast.Store())], value=ast.Constant(value=0))

        enc_for = ast.For(
            target=ast.Name(id='b', ctx=ast.Store()),
            iter=ast.Name(id=self.data_var, ctx=ast.Load()),
            body=[
                ast.Assign(
                    targets=[ast.Name(id=self.i_var, ctx=ast.Store())],
                    value=ast.BinOp(left=ast.Name(id=self.i_var, ctx=ast.Load()), op=ast.Add(), right=ast.Constant(value=1))
                ),
                ast.Assign(
                    targets=[ast.Name(id=self.j_var, ctx=ast.Store())],
                    value=ast.BinOp(
                        left=ast.Name(id=self.j_var, ctx=ast.Load()),
                        op=ast.Add(),
                        right=ast.Subscript(value=ast.Name(id=self.s_table_var, ctx=ast.Load()), slice=ast.Name(id=self.i_var, ctx=ast.Load()), ctx=ast.Load())
                    )
                ),
                ast.Assign(
                    targets=[ast.Tuple(elts=[
                        ast.Subscript(value=ast.Name(id=self.s_table_var, ctx=ast.Load()), slice=ast.Name(id=self.i_var, ctx=ast.Load()), ctx=ast.Store()),
                        ast.Subscript(value=ast.Name(id=self.s_table_var, ctx=ast.Load()), slice=ast.Name(id=self.j_var, ctx=ast.Store()), ctx=ast.Store())
                    ], ctx=ast.Store())],
                    value=ast.Tuple(
                        elts=[
                            ast.Subscript(value=ast.Name(id=self.s_table_var, ctx=ast.Load()), slice=ast.Name(id=self.j_var, ctx=ast.Load()), ctx=ast.Load()),
                            ast.Subscript(value=ast.Name(id=self.s_table_var, ctx=ast.Load()), slice=ast.Name(id=self.i_var, ctx=ast.Load()), ctx=ast.Load())
                        ],
                        ctx=ast.Load()
                    )
                ),
                ast.Assign(
                    targets=[ast.Name(id=self.k_var, ctx=ast.Store())],
                    value=ast.Subscript(
                        value=ast.Name(id=self.s_table_var, ctx=ast.Load()),
                        slice=ast.BinOp(
                            left=ast.BinOp(
                                left=ast.Name(id=self.s_table_var, ctx=ast.Load()),
                                op=ast.Add(),
                                right=ast.Name(id=self.s_table_var, ctx=ast.Load())
                            ),
                            op=ast.Mod(),
                            right=ast.Constant(value=256)
                        ),
                        ctx=ast.Load()
                    )
                ),
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(value=ast.Name(id=self.out_var, ctx=ast.Load()), attr='append', ctx=ast.Load()),
                        args=[ast.BinOp(left=ast.Name(id='b', ctx=ast.Load()), op=ast.BitXor(), right=ast.Name(id=self.k_var, ctx=ast.Load()))],
                        keywords=[]
                    )
                )
            ],
            orelse=[]
        )

        # 最終比較結果を return
        ret_stmt = ast.Return(
            value=ast.Compare(
                left=ast.Name(id=self.out_var, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Name(id=self.target_var, ctx=ast.Load())]
            )
        )

        func_def = ast.FunctionDef(
            name=self.func_name,
            args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
            body=[key_assign, data_assign, target_assign, s_init, ast.Assign(targets=[ast.Name(id=self.j_var, ctx=ast.Store())], value=ast.Constant(value=0)),
                  ksa_loop, i_assign, j_assign, enc_loop, enc_for, ret_stmt],
            decorator_list=[]
        )

        return func_def
