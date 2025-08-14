import ast
import random
import string
from dead_code_generator import DeadCodeGenerator
from string_obfuscator import CompiledStringObfuscator as HardStringObfuscator
from control_flow_flattener import ControlFlowFlattener
from single_statement_flattener import SingleStatementFlattener

class UltraMassiveObfuscator:
    def __init__(self, flatten_repeat=50, string_obf_repeat=50, dummy_repeat=100, nest_depth=20, available_vars=None):
        self.flatten_repeat = flatten_repeat
        self.string_obf_repeat = string_obf_repeat
        self.dummy_repeat = dummy_repeat
        self.nest_depth = nest_depth
        if available_vars is None:
            self.available_vars = ['var_' + ''.join(random.choices(string.ascii_letters, k=5)) for _ in range(50)]
        else:
            self.available_vars = available_vars
        self.dead_code_gen = DeadCodeGenerator(self.available_vars)

    def _insert_dummy_vars(self, tree):
        assigns = []
        for var in self.available_vars:
            assigns.append(
                ast.Assign(
                    targets=[ast.Name(id=var, ctx=ast.Store())],
                    value=ast.Constant(value=random.randint(0, 100))
                )
            )
        tree.body = assigns + tree.body
        return tree


    def _generate_dummy_func(self):
        name = ''.join(random.choices(string.ascii_letters, k=12))
        arg = ''.join(random.choices(string.ascii_letters, k=5))
        var = ''.join(random.choices(string.ascii_letters, k=6))
        loop_limit = random.randint(5, 15)
        increment = random.choice([1, 2, 3])
        threshold = random.randint(50, 150)
        body_code = f"""def {name}({arg}):
    {var} = 0
    if {arg} > {random.randint(0, 5)}: {var} += {random.randint(1, 3)}
    else: {var} -= {random.randint(1, 3)}
    i = 0
    while i < {loop_limit}:
        if i % {random.choice([2,3,4])} == 0: {var} += i * {increment}
        else: {var} -= i
        i += {increment}
    for j in range({random.randint(1, loop_limit)}):
        if j == {loop_limit} // {random.choice([2,3,4])}: continue
        {var} += j
    while {var} < {threshold}: {var} += {increment}
    return {var}
"""
        return ast.parse(body_code).body[0]

    def _generate_dummy_assign(self):
        var = random.choice(self.available_vars)
        val = random.randint(0, 50)
        return ast.Assign(targets=[ast.Name(id=var, ctx=ast.Store())], value=ast.Constant(value=val))

    def _add_nested_ifs(self, node):
        assign_count = random.randint(1, 5)
        assigns = [self._generate_dummy_assign() for _ in range(assign_count)]
        current = node
        for i in range(self.nest_depth):
            if i == self.nest_depth - random.randint(1, 10):
                body = assigns + ([current] if isinstance(current, ast.AST) else current)
            else:
                body = [current] if isinstance(current, ast.AST) else current
            current = ast.If(test=self.dead_code_gen.random_true_condition(), body=body, orelse=[])
        return current

    def apply(self, tree):
        for _ in range(self.dummy_repeat):
            dummy = self._generate_dummy_func()
            tree.body.insert(0, dummy)

        for _ in range(self.string_obf_repeat):
            tree = HardStringObfuscator().visit(tree)
            ast.fix_missing_locations(tree)

        for _ in range(self.flatten_repeat):
            tree = ControlFlowFlattener().visit(tree)
            ast.fix_missing_locations(tree)
            tree = SingleStatementFlattener().visit(tree)
            ast.fix_missing_locations(tree)

        new_body = []
        for stmt in tree.body:
            new_body.append(self._add_nested_ifs(stmt))
        tree.body = [self._add_nested_ifs(stmt) for stmt in tree.body]

        # 変数の定義を必ず先頭に入れておく（NameError防止）
        tree = self._insert_dummy_vars(tree)

        ast.fix_missing_locations(tree)
        return tree