import ast
import sys

# 各種難読化クラスをインポート
from control_flow_flattener import ControlFlowFlattener
from decode_call_inliner import DecodeCallInliner
from string_obfuscator import HardStringObfuscator
from number_obfuscator import NumberObfuscator
from single_statement_flattener import SingleStatementFlattener
from function_renamer import FunctionRenamer
from ultra_massive_obfuscator import UltraMassiveObfuscator

def obfuscate_python_file(file_path, output_path=None):
    """
    指定されたPythonファイルを難読化します。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # --- 元のコードのロジックに関する注記 ---
    # 元のコードでは、以下の難読化処理群の後に `tree = ast.parse(source_code)` が
    # 再度実行されていました。これにより、ここで行われる変更はすべて破棄され、
    # 最終的な出力には反映されていませんでした。
    #
    # このリファクタリングでは、元のコードの動作を維持するため、そのロジックを
    # そのままにしていますが、これは意図しない動作である可能性があります。
    # 実際に効果を適用するには、`tree = ast.parse(source_code)` の行を
    # 削除し、各処理を連鎖的に適用する必要があります。
    # -----------------------------------------

    # AST 解析
    tree = ast.parse(source_code)

    # 1. 制御フローのフラット化
    tree = ControlFlowFlattener().visit(tree)
    ast.fix_missing_locations(tree)

    # 2. デコード関数のインライン化
    tree = DecodeCallInliner().visit(tree)
    ast.fix_missing_locations(tree)

    # 3. 文字列の難読化
    tree = HardStringObfuscator().visit(tree)
    ast.fix_missing_locations(tree)

    # 4. 数値の難読化
    tree = NumberObfuscator().visit(tree)
    ast.fix_missing_locations(tree)

    # 5. 単一文のフラット化
    tree = SingleStatementFlattener().visit(tree)
    ast.fix_missing_locations(tree)

    # 6. 関数名のリネーム
    tree = FunctionRenamer().visit(tree)
    ast.fix_missing_locations(tree)


    # 元のコードのロジックに従い、ここでASTを再生成します。
    # 注意: この行により、上記で行われた全ての変更が破棄されます。
    tree = ast.parse(source_code)

    # 7. 最終的な大規模難読化を適用
    over_obf = UltraMassiveObfuscator(flatten_repeat=40, string_obf_repeat=40, dummy_repeat=40)
    tree = over_obf.apply(tree)

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