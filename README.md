# seccamp2025

Pythonコードを対象とした **AST（抽象構文木）ベースの難読化ツール** です。
識別子リネーム・文字列難読化・コード冗長化を中心に、生成aiを騙すことを目標として開発しました。

---

## 特徴

* Python標準の `ast` モジュールを用いた構文解析
* 構文を壊さずに安全なリネーム処理
* 可読性を極端に低下させる文字列・構造変換
* コード行数を大幅に増加させる冗長化処理

---

## 対応している難読化機能

* グローバル変数のリネーム
* クラス名のリネーム
* メソッド名のリネーム
* クラス属性（`self.xxx`）のリネーム
* コメント削除
* 文字列難読化

  * `ord()` / `chr()` ベース変換
  * オフセット方式＋復号関数化
* 無意味なコード膨張（フラット化・ダミーコード挿入）

---

## 非対応・制限事項

* `__init__` などの **特殊メソッド名の変更**（できない😭）
* Python外部モジュールの挙動保証
* 高度な動的コード（`eval`, `exec` 多用コード）

---

## 動作環境

* Python 3.9 以降（推奨）
* 追加ライブラリ不要（標準ライブラリのみ）

---

## ディレクトリ構成

```
.
├── __pycache__
│   ├── control_flow_flattener.cpython-313.pyc
│   ├── dead_code_generator.cpython-313.pyc
│   ├── decode_call_inliner.cpython-313.pyc
│   ├── dummy_bytecode_injector.cpython-313.pyc
│   ├── function_renamer.cpython-313.pyc
│   ├── make_compile_encoded_string.cpython-313.pyc
│   ├── make_string.cpython-313.pyc
│   ├── match_Flattener.cpython-313.pyc
│   ├── number_obfuscator.cpython-313.pyc
│   ├── rc4_checker_generator.cpython-313.pyc
│   ├── single_statement_flattener.cpython-313.pyc
│   ├── string_obfuscator.cpython-313.pyc
│   ├── substring_splitter.cpython-313.pyc
│   ├── substringpslitter.cpython-313.pyc
│   ├── ultra_massive_obfuscator.cpython-313.pyc
│   └── utils.cpython-313.pyc
├── builtin_obfuscator.py
├── control_flow_flattener.py
├── dead_code_generator.py
├── decode_call_inliner.py
├── dummy_bytecode_injector.py
├── function_renamer.py
├── main.py
├── match_Flattener.py
├── number_obfuscator.py
├── output.py
├── rc4_checker_generator.py
├── sample.py
├── single_statement_flattener.py
├── string_obfuscator.py
├── substringpslitter.py
├── ultra_massive_obfuscator.py
└── utils.py
```

---

## 使い方

### 難読化対象ファイルの準備

```bash
python obfuscator.py input.py output.py
```

* `input.py` : 難読化したいPythonファイル
* `output.py`: 難読化後の出力ファイル

---

## 設計方針

* 意味は保つが、理解しづらくする
* AST変換により構文破壊を防止
* 解析者の思考・静的解析ツールの両方を妨害

---

## 想定用途

* 難読化技術の学習・研究
* 解析不能コード生成の検証

---
