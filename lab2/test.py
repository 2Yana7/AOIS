import unittest
import itertools
from io import StringIO
import sys
from lab2 import (
    preprocess_expression, tokenize, shunting_yard, rpn_to_ast, parse_expression,
    label_sub_expressions, compute_depth, evaluate_ast, collect_sub_expressions_in_order, Node,
    generate_truth_table_and_forms, main
)

class TestLogicExpressions(unittest.TestCase):

    def setUp(self):
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_preprocess_expression(self):
        self.assertEqual(preprocess_expression("a & b"), "a&b")
        self.assertEqual(preprocess_expression("  a->b  "), "a->b")
        self.assertEqual(preprocess_expression("a  |  b"), "a|b")
        self.assertEqual(preprocess_expression("a~b"), "a~b")

    def test_tokenize(self):
        self.assertEqual(tokenize("a&(b|c)"), ['a', '&', '(', 'b', '|', 'c', ')'])
        self.assertEqual(tokenize("a->b"), ['a', '->', 'b'])
        self.assertEqual(tokenize("a~b"), ['a', '~', 'b'])
        self.assertEqual(
            tokenize("(a|c)&(b|d)~b"),
            ['(', 'a', '|', 'c', ')', '&', '(', 'b', '|', 'd', ')', '~', 'b']
        )
        self.assertEqual(tokenize("a"), ['a'])

    def test_shunting_yard(self):
        tokens = tokenize("a&(b|c)")
        rpn = shunting_yard(tokens)
        self.assertEqual(rpn, ['a', 'b', 'c', '|', '&'])
        tokens = tokenize("a->b")
        rpn = shunting_yard(tokens)
        self.assertEqual(rpn, ['a', 'b', '->'])
        tokens = tokenize("a~b")
        rpn = shunting_yard(tokens)
        self.assertEqual(rpn, ['a', 'b', '~'])
        tokens = tokenize("a|(b&c)")
        rpn = shunting_yard(tokens)
        self.assertEqual(rpn, ['a', 'b', 'c', '&', '|'])

    def test_rpn_to_ast(self):
        rpn = ['a', 'b', 'c', '|', '&']
        ast = rpn_to_ast(rpn)
        label_sub_expressions(ast)
        self.assertEqual(ast.expr_str, "a∧(b∨c)")

        rpn = ['a', 'b', '->']
        ast = rpn_to_ast(rpn)
        label_sub_expressions(ast)
        self.assertEqual(ast.expr_str, "a→b")

        rpn = ['a', 'b', '~']
        ast = rpn_to_ast(rpn)
        label_sub_expressions(ast)
        self.assertEqual(ast.expr_str, "a↔b")

        rpn = ['a', 'b', 'c', '&', '|']
        ast = rpn_to_ast(rpn)
        label_sub_expressions(ast)
        self.assertEqual(ast.expr_str, "a∨(b∧c)")

    def test_evaluate_ast(self):
        ast = parse_expression("a&(b|c)")
        label_sub_expressions(ast)
        env = {'a': True, 'b': False, 'c': True}
        self.assertTrue(evaluate_ast(ast, env))
        env = {'a': True, 'b': False, 'c': False}
        self.assertFalse(evaluate_ast(ast, env))

        ast = parse_expression("a->b")
        label_sub_expressions(ast)
        env = {'a': True, 'b': False}
        self.assertFalse(evaluate_ast(ast, env))
        env = {'a': False, 'b': False}
        self.assertTrue(evaluate_ast(ast, env))

        ast = parse_expression("a~b")
        label_sub_expressions(ast)
        env = {'a': True, 'b': True}
        self.assertTrue(evaluate_ast(ast, env))
        env = {'a': True, 'b': False}
        self.assertFalse(evaluate_ast(ast, env))

        ast = parse_expression("a|(b&(c->d))")
        label_sub_expressions(ast)
        env = {'a': True, 'b': True, 'c': True, 'd': False}
        self.assertTrue(evaluate_ast(ast, env))

    def test_compute_depth(self):
        ast = parse_expression("a&(b|c)")
        label_sub_expressions(ast)
        depth = compute_depth(ast)
        self.assertEqual(depth, 3)

        ast = parse_expression("a->(b&(c|d))")
        label_sub_expressions(ast)
        depth = compute_depth(ast)
        self.assertEqual(depth, 4)

    def test_collect_sub_expressions(self):
        ast = parse_expression("a&(b|c)")
        label_sub_expressions(ast)
        nodes = collect_sub_expressions_in_order(ast)
        exprs = [node.expr_str for node in nodes]
        self.assertIn("a", exprs)
        self.assertIn("b", exprs)
        self.assertIn("c", exprs)
        self.assertIn("b∨c", exprs)
        self.assertIn("a∧(b∨c)", exprs)

        ast = parse_expression("a->(b&(c|d))")
        label_sub_expressions(ast)
        nodes = collect_sub_expressions_in_order(ast)
        exprs = [node.expr_str for node in nodes]
        self.assertIn("a", exprs)
        self.assertIn("b", exprs)
        self.assertIn("c", exprs)
        self.assertIn("d", exprs)
        self.assertIn("b∧(c∨d)", exprs)

    def test_generate_truth_table_and_forms(self):
        expr = "(a|b)&(c|d)"
        ast = parse_expression(expr)
        label_sub_expressions(ast)
        self.assertEqual(ast.expr_str, "(a∨b)∧(c∨d)")

        all_nodes = collect_sub_expressions_in_order(ast)
        var_nodes = [n for n in all_nodes if n.node_type == 'var']
        complex_nodes = [n for n in all_nodes if n.node_type != 'var']
        var_nodes_sorted = sorted(var_nodes, key=lambda n: n.var)
        self.assertEqual([n.var for n in var_nodes_sorted], ['a', 'b', 'c', 'd'])

        header = " | ".join(node.expr_str for node in var_nodes_sorted + complex_nodes + [ast])
        self.assertIn('a', header)
        self.assertIn('b', header)
        self.assertIn('c', header)
        self.assertIn('d', header)
        self.assertIn('a∨b', header)

        vars_sorted = [n.var for n in var_nodes_sorted]
        n_vars = len(vars_sorted)
        truth_rows = []
        for combo in itertools.product([0, 1], repeat=n_vars):
            env = {var: bool(val) for var, val in zip(vars_sorted, combo)}
            f_val = 1 if evaluate_ast(ast, env) else 0
            truth_rows.append((combo, f_val))
        self.assertEqual(len(truth_rows), 16)

        minterms = []
        maxterms = []
        for combo, f_val in truth_rows:
            index = int("".join(str(bit) for bit in combo), 2)
            if f_val == 1:
                minterms.append(index)
            else:
                maxterms.append(index)
        self.assertIn(5, minterms)
        self.assertIn(0, maxterms)

        dnf_terms = []
        cnf_terms = []
        for combo, f_val in truth_rows:
            term_literals = []
            for bit, var in zip(combo, vars_sorted):
                term_literals.append(var if bit == 1 else "¬" + var)
            if f_val == 1:
                dnf_terms.append("(" + "∧".join(term_literals) + ")")
            else:
                cnf_terms.append("(" + "∨".join(term_literals) + ")")
        dnf_formula = " ∨ ".join(dnf_terms)
        cnf_formula = " ∧ ".join(cnf_terms)
        self.assertNotEqual(dnf_formula, "")

        index_bits = []
        for combo, f_val in truth_rows:
            index_bits.append("1" if f_val else "0")
        binary_str = "".join(index_bits)
        index_value = int(binary_str, 2)
        binary_str_padded = format(index_value, f"0{2 ** n_vars}b")
        self.assertEqual(binary_str_padded, '0000011101110111')
        self.assertEqual(index_value, 1911)

    def test_simple_expression(self):
        expr = "a & b"
        result = generate_truth_table_and_forms(expr)
        self.assertEqual(result['minterms'], [3])
        self.assertEqual(result['maxterms'], [0, 1, 2])
        self.assertEqual(result['dnf_formula'], "(a∧b)")
        self.assertEqual(result['cnf_formula'], "(a∨b) ∧ (a∨¬b) ∧ (¬a∨b)")
        self.assertEqual(result['index_value'], 1)
        self.assertEqual(result['binary_str_padded'], '0001')

    def test_complex_expression(self):
        expr = "(a | b) & (c | d)"
        result = generate_truth_table_and_forms(expr)
        self.assertIn(15, result['minterms'])
        self.assertIn(14, result['minterms'])
        self.assertIn(13, result['minterms'])
        self.assertIn(11, result['minterms'])
        self.assertIn(7, result['minterms'])
        self.assertEqual(result['index_value'], 1911)
        self.assertEqual(result['binary_str_padded'], '0000011101110111')

    def test_complex_nested_expressions(self):
        expr = "!!a->(b&(c|!d))"
        ast = parse_expression(expr)
        label_sub_expressions(ast)
        self.assertEqual(ast.expr_str, "¬¬a→(b∧(c∨¬d))")

        depth = compute_depth(ast)
        self.assertEqual(depth, 5)

    def test_mixed_operators_priority(self):
        expr = "a|b&c"
        ast = parse_expression(expr)
        label_sub_expressions(ast)
        self.assertEqual(ast.expr_str, "a∨(b∧c)")

class TestMainFunction(unittest.TestCase):
    def test_main_function(self):
        captured_output = StringIO()
        sys.stdout = captured_output

        input_mock = lambda _: "(a | b) & (c | d)"
        original_input = __builtins__.input
        __builtins__.input = input_mock

        main()

        __builtins__.input = original_input
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Таблица истинности с подвыражениями", output)
        self.assertIn("Совершенная дизъюнктивная нормальная форма (СДНФ)", output)
        self.assertIn("Совершенная конъюнктивная нормальная форма (СКНФ)", output)
        self.assertIn("Индексная форма", output)

if __name__ == '__main__':
    unittest.main()