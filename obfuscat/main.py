import ast
import sys


# 各種難読化クラスをインポート
from control_flow_flattener import ControlFlowFlattener
from decode_call_inliner import DecodeCallInliner
from string_obfuscator import CompiledStringObfuscator as HardStringObfuscator
from number_obfuscator import NumberObfuscator
from single_statement_flattener import SingleStatementFlattener
from function_renamer import FunctionRenamer
from ultra_massive_obfuscator import UltraMassiveObfuscator
from match_Flattener import MatchFlattener
from substringpslitter import SubstringSplitter
from rc4_checker_generator import RC4CheckGenerator

def obfuscate_python_file(file_path, output_path=None):
    """
    指定されたPythonファイルを難読化します。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()


    # AST 解析
    tree = ast.parse(source_code)

        # RC4チェック関数生成
    key_bytes = b"mysecretkey"
    check_data = b"checkdata"
    target_bytes = b"expectedoutput"
    rc4_gen = RC4CheckGenerator(key_bytes, check_data, target_bytes)
    rc4_func_ast = rc4_gen.generate()

    # AST の先頭に追加
    tree.body.insert(0, rc4_func_ast)

    # 1. 制御フローのフラット化
    tree = ControlFlowFlattener().visit(tree)
    ast.fix_missing_locations(tree)

    # 2. デコード関数のインライン化と分割
    tree = DecodeCallInliner().visit(tree)#    ast.fix_missing_locations(tree)
    tree = SubstringSplitter().visit(tree)
    ast.fix_missing_locations(tree)

    # 3. 文字列の難読化
    tree = HardStringObfuscator().visit(tree)
    ast.fix_missing_locations(tree)

    # 4. 数値の難読化
    tree = NumberObfuscator().visit(tree)
    ast.fix_missing_locations(tree)

    # 5. 単一文のフラット化
    tree = ControlFlowFlattener().visit(tree)
    ast.fix_missing_locations(tree)
    tree = SingleStatementFlattener().visit(tree)
    ast.fix_missing_locations(tree)

    # 6. 関数名のリネーム
    tree = FunctionRenamer().visit(tree)
    ast.fix_missing_locations(tree)

    # 7. match文によるフラット化
    tree = MatchFlattener().visit(tree)
    ast.fix_missing_locations(tree)

    # 8. 色々
    over_obf = UltraMassiveObfuscator(flatten_repeat=40, string_obf_repeat=40, dummy_repeat=40)
    tree = over_obf.apply(tree)
    ast.fix_missing_locations(tree)

    # ASTをPythonコードへ変換
    new_code = ast.unparse(tree)

    # ファイルへの書き込み
    if output_path is None:
        output_path = file_path  # 指定がない場合は上書き
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    obfuscate_python_file(input_file, output_file)