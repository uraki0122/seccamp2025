import random
import string

# このモジュールは、ランダムな英字の文字列を生成するための関数を作成

def generate_random_name(length=8):
    """指定された長さのランダムな英字の文字列を生成します。"""
    return ''.join(random.choices(string.ascii_letters, k=length))