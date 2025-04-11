import unittest
import io
import sys
import time
from contextlib import redirect_stdout
import lab3


class TestLab3Functions(unittest.TestCase):
    def setUp(self):
        self._stdout = sys.stdout
        sys.stdout = io.StringIO()

    def tearDown(self):
        sys.stdout = self._stdout

    def test_preprocess_expression(self):
        expr = " a -> (b & c) "
        processed = lab3.preprocess_expression(expr)
        self.assertEqual(processed, "a->(b&c)")

    def test_tokenize(self):
        expr = "a -> b"
        tokens = lab3.tokenize(expr)
        self.assertEqual(tokens, ['a', '->', 'b'])

    def test_shunting_yard(self):
        tokens = ['a', '->', 'b']
        rpn = lab3.shunting_yard(tokens)
        self.assertEqual(rpn, ['a', 'b', '->'])

    def test_rpn_to_ast_unary(self):
        rpn = ["a", "!"]
        ast = lab3.rpn_to_ast(rpn)
        self.assertEqual(ast.node_type, "not")
        self.assertEqual(ast.left.node_type, "var")
        self.assertEqual(ast.left.var, "a")

    def test_parse_expression(self):
        expr = "a->b"
        ast = lab3.parse_expression(expr)
        self.assertEqual(ast.node_type, "implies")
        self.assertEqual(ast.left.node_type, "var")
        self.assertEqual(ast.left.var, "a")
        self.assertEqual(ast.right.node_type, "var")
        self.assertEqual(ast.right.var, "b")

    def test_label_sub_expressions(self):
        expr = "a|b"
        ast = lab3.parse_expression(expr)
        lab3.label_sub_expressions(ast)
        self.assertIn("∨", ast.expr_str)

    def test_compute_depth(self):
        expr = "a->b"
        ast = lab3.parse_expression(expr)
        depth = lab3.compute_depth(ast)
        self.assertEqual(depth, 2)

    def test_collect_sub_expressions_in_order(self):
        expr = "a&b"
        ast = lab3.parse_expression(expr)
        lab3.label_sub_expressions(ast)
        subs = lab3.collect_sub_expressions_in_order(ast)
        self.assertEqual(len(subs), 3)

    def test_evaluate_ast(self):
        expr = "a&b"
        ast = lab3.parse_expression(expr)
        env = {"a": True, "b": False}
        result = lab3.evaluate_ast(ast, env)
        self.assertFalse(result)

    def test_generate_truth_table_and_forms(self):
        expr = "a"
        with redirect_stdout(io.StringIO()):
            fdata = lab3.generate_truth_table_and_forms(expr)
        expected_keys = {'minterms', 'maxterms', 'dnf_formula', 'cnf_formula',
                         'index_value', 'binary_str_padded', 'vars_sorted',
                         'n_vars', 'ast'}
        self.assertTrue(expected_keys.issubset(fdata.keys()))

    def test_group_to_term_dnf(self):
        group = ((0, 0), (0, 0))
        grid = [[1]]
        row_labels = ["a=1"]
        col_labels = ["b=1"]
        var_names = ["a", "b"]
        term = lab3.group_to_term(group, grid, row_labels, col_labels, var_names, 2, for_dnf=True)
        self.assertEqual(term, "a∧b")

    def test_int_to_bin_str(self):
        result = lab3.int_to_bin_str(5, 3)
        self.assertEqual(result, "101")

    def test_combine_terms(self):
        res = lab3.combine_terms("101", "100")
        self.assertEqual(res, "10-")
        res2 = lab3.combine_terms("101", "111")
        self.assertEqual(res2, "1-1")
        a = (1, 0, 1)
        c = (0, 0, 1)
        merged_none = lab3._merge_pair(a, c)
        self.assertEqual(merged_none, ('-', 0, 1))

    def test_bin_to_lits(self):
        res = lab3.bin_to_lits("1-0", ["a", "b", "c"], is_dnf=True)
        self.assertEqual(res, "a∧¬c")

    def test_literal_set_from_binary(self):
        res = lab3.literal_set_from_binary("1-0", ["a", "b", "c"], True)
        self.assertEqual(res, {"a", "¬c"})

    def test_covers(self):
        self.assertTrue(lab3.covers("1-0", "100"))
        self.assertTrue(lab3.covers("1-0", "110"))
        self.assertFalse(lab3.covers("1-0", "101"))

    def test_eliminate_redundant_implicants(self):
        implicants = ["1-0", "110"]
        terms = [int("100", 2), int("110", 2)]
        reduced = lab3.eliminate_redundant_implicants(implicants, terms, 3)
        self.assertTrue(len(reduced) > 0)

    def test_absorb_clauses(self):
        implicants = ["1-0", "110"]
        absorbed = lab3.absorb_clauses(implicants, ["a", "b", "c"], False)
        self.assertTrue(len(absorbed) > 0)

    def test_quine_mccluskey_calc(self):
        minterms = [1, 2, 3]
        implicants = lab3.quine_mccluskey_calc(minterms, 2, ["a", "b"], True)
        self.assertTrue(isinstance(implicants, list))
        self.assertTrue(len(implicants) > 0)

    def test_select_essential_calc(self):
        primes = ["1-0", "110"]
        minterms = [int("100", 2), int("110", 2)]
        essential = lab3.select_essential_calc(primes, minterms, 3, ["a", "b", "c"], True)
        self.assertTrue(set(essential).issubset(set(primes)))

    def test_minimize_calc_dnf(self):
        with redirect_stdout(io.StringIO()):
            data = lab3.generate_truth_table_and_forms("a")
            minimized = lab3.minimize_calc_dnf(data['minterms'], data['n_vars'], data['vars_sorted'])
        self.assertIsInstance(minimized, str)
        self.assertTrue(len(minimized) > 0)

    def test_minimize_calc_cnf(self):
        with redirect_stdout(io.StringIO()):
            data = lab3.generate_truth_table_and_forms("a")
            minimized = lab3.minimize_calc_cnf(data['maxterms'], data['n_vars'], data['vars_sorted'])
        self.assertIsInstance(minimized, str)
        self.assertTrue(len(minimized) > 0)

    def test_term_to_clause(self):
        clause = lab3.term_to_clause(1, ["a", "b"], for_cnf=True)
        self.assertEqual(clause, "(a∨¬b)")

    def test_quine_mccluskey_tabular(self):
        minterms = [0, 1, 2, 3]
        primes = lab3.quine_mccluskey_tabular(minterms, 2, ["a", "b"], True)
        self.assertTrue(isinstance(primes, list))
        self.assertTrue(len(primes) > 0)

    def test_minimize_tab_dnf(self):
        with redirect_stdout(io.StringIO()):
            data = lab3.generate_truth_table_and_forms("a")
            minimized = lab3.minimize_tab_dnf(data['minterms'], data['n_vars'], data['vars_sorted'])
        self.assertIsInstance(minimized, str)

    def test_minimize_tab_cnf(self):
        with redirect_stdout(io.StringIO()):
            data = lab3.generate_truth_table_and_forms("a")
            minimized = lab3.minimize_tab_cnf(data['maxterms'], data['n_vars'], data['vars_sorted'])
        self.assertIsInstance(minimized, str)

    def test_listRectangles(self):
        matrix = [[1, 1], [1, 0]]
        rects = lab3.listRectangles(matrix, 2)
        self.assertTrue(isinstance(rects, list))
        self.assertTrue(len(rects) > 0)

    def test_listZeroRectangles(self):
        matrix = [[0, 1], [1, 0]]
        rects = lab3.listZeroRectangles(matrix, 2)
        self.assertTrue(isinstance(rects, list))

    def test_extractCells(self):
        rect = ((0, 0), (1, 1))
        cells = lab3.extractCells(rect, 2, 2, 2)
        self.assertEqual(cells, {(0, 0), (0, 1), (1, 0), (1, 1)})

    def test_selectCover(self):
        candidates = [(((0, 0), (0, 0)), "a"), (((0, 1), (0, 1)), "b")]
        onesSet = {(0, 0)}
        selected = lab3.selectCover(candidates, onesSet, 2, 1, 2)
        self.assertIsInstance(selected, list)

    def test_selectZeroCover(self):
        candidates = [(((0, 0), (0, 0)), "a"), (((0, 1), (0, 1)), "b")]
        zerosSet = {(0, 1)}
        selected = lab3.selectZeroCover(candidates, zerosSet, 2, 1, 2)
        self.assertIsInstance(selected, list)

    def test_gray_code(self):
        code = lab3.gray_code(3)
        expected = [i ^ (i >> 1) for i in range(8)]
        self.assertEqual(code, expected)

    def test__to_binary_terms(self):
        terms = [1, 2]
        result = lab3._to_binary_terms(terms, 3)
        self.assertEqual(result, [(0, 0, 1), (0, 1, 0)])

    def test__merge_pair(self):
        a = (1, 0, 1)
        b = (1, 1, 1)
        merged = lab3._merge_pair(a, b)
        self.assertEqual(merged, (1, '-', 1))

    def test__find_prime_implicants(self):
        terms = [(0, 0), (0, 1), (1, 0), (1, 1)]
        primes = lab3._find_prime_implicants(terms, 2)
        self.assertTrue(isinstance(primes, set))
        self.assertTrue(len(primes) > 0)

    def test__covers(self):
        self.assertTrue(lab3._covers((1, '-', 0), (1, 0, 0)))
        self.assertFalse(lab3._covers((1, '-', 0), (0, 0, 0)))

    def test__select_essential(self):
        primes = {(1, '-', 0), (1, 0, 0)}
        minterms = [(1, 0, 0), (1, 1, 0)]
        essentials = lab3._select_essential(primes, minterms)
        self.assertTrue(isinstance(essentials, set))

    def test_kmap_minimize(self):
        terms = [1]
        minimized = lab3.kmap_minimize(terms, 1, ["a"], is_dnf=True)
        self.assertTrue(isinstance(minimized, list))

    def test_print_kmap_table(self):
        f = io.StringIO()
        with redirect_stdout(f):
            lab3.print_kmap_table([1], 1, ["a"], is_dnf=True)
        output = f.getvalue()
        self.assertIn("a", output)

    def test_main(self):
        saved_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO("a->b\n")
            f = io.StringIO()
            with redirect_stdout(f):
                lab3.main()
            output = f.getvalue()
            self.assertIn("Введите логическое выражение", output)
            self.assertIn("Таблица истинности", output)
            self.assertIn("Результаты минимизации", output)
        finally:
            sys.stdin = saved_stdin


class MinimalTextTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)

    def printErrors(self):
        pass


class MinimalTestRunner(unittest.TextTestRunner):
    resultclass = MinimalTextTestResult

    def run(self, test):
        start = time.time()
        result = super().run(test)
        t = time.time() - start
        sys.stdout.write(f"Ran {result.testsRun} tests in {t:.3f}s")
        return result


if __name__ == "__main__":
    unittest.main(testRunner=MinimalTestRunner, exit=False)
