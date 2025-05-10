import unittest
import random
import io
import sys

from matrix import (
    diagonal_to_linear_index,
    create_binary_diagonal_matrix,
    get_value,
    set_value,
    print_matrix,
    get_word,
    get_addressed_column,
)
from logic_fun import f0, f5, f10, f15
from sum import binary_add_4bit


class TestMatrixFunctions(unittest.TestCase):

    def test_diagonal_to_linear_index(self):
        N = 4
        self.assertEqual(diagonal_to_linear_index(0, 0, N), 0)
        self.assertEqual(diagonal_to_linear_index(0, 1, N), 1)
        self.assertEqual(diagonal_to_linear_index(1, 0, N), 2)
        self.assertEqual(diagonal_to_linear_index(1, 1, N), 4)
        for i in range(N):
            for j in range(N):
                idx = diagonal_to_linear_index(i, j, N)
                self.assertTrue(0 <= idx < N*N)

    def test_create_set_get_value(self):
        random.seed(42)
        N = 8
        flat = create_binary_diagonal_matrix(N)
        self.assertEqual(len(flat), N*N)
        self.assertTrue(all(bit in (0, 1) for bit in flat))
        i, j = 2, 3
        orig = get_value(flat, i, j, N)
        new = 1 - orig
        set_value(flat, i, j, new, N)
        self.assertEqual(get_value(flat, i, j, N), new)

    def test_print_matrix_all_ones(self):
        N = 4
        flat = [1] * (N * N)
        buf = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buf
        try:
            print_matrix(flat, N)
        finally:
            sys.stdout = sys_stdout
        lines = buf.getvalue().strip().splitlines()
        self.assertEqual(len(lines), N)
        for line in lines:
            parts = line.split()
            self.assertEqual(len(parts), N)
            self.assertTrue(all(val == '1' for val in parts))

    def test_print_matrix_non_square_raises(self):
        with self.assertRaises(Exception):
            print_matrix([0,1,2], 2)

    def test_get_word_and_addressed_column(self):
        N = 5
        flat = list(range(N*N))
        col = 2
        w = get_word(flat, col, N)
        expected = [get_value(flat, (i+col) % N, col, N) for i in range(N)]
        self.assertEqual(w, expected)
        idx = 3
        c = get_addressed_column(flat, idx, N)
        expected_c = [get_value(flat, (idx+i) % N, i, N) for i in range(N)]
        self.assertEqual(c, expected_c)


class TestLogicFun(unittest.TestCase):

    def test_f0(self):
        self.assertEqual(f0([0,1,1,0]), [0,0,0,0])

    def test_f5(self):
        self.assertEqual(f5([0,1,1,0]), [0,1,1,0])

    def test_f10(self):
        self.assertEqual(f10([0,1,1,0]), [1,0,0,1])

    def test_f15(self):
        self.assertEqual(f15([0,1,1,0]), [1,1,1,1])

    def test_logic_fun_empty(self):
        for fn in (f0, f5, f10, f15):
            self.assertEqual(fn([]), [])

    def test_f10_double_negation(self):
        data = [random.randint(0,1) for _ in range(8)]
        self.assertEqual(f10(f10(data)), data)

    def test_logic_fun_output_length(self):
        data = [random.randint(0,1) for _ in range(7)]
        for fn in (f0, f5, f10, f15):
            self.assertEqual(len(fn(data)), len(data))

    def test_f5_copy_independence(self):
        data = [0,1,0]
        out = f5(data)
        data[0] = 1
        self.assertNotEqual(data, out)


class TestBinaryAdd4Bit(unittest.TestCase):

    def check(self, a, b, expected):
        res = binary_add_4bit(a, b)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 5)
        self.assertTrue(all(bit in (0,1) for bit in res))
        self.assertEqual(res, expected)



    def test_binary_add_random(self):
        for _ in range(10):
            a = [random.randint(0,1) for _ in range(4)]
            b = [random.randint(0,1) for _ in range(4)]
            res = binary_add_4bit(a,b)
            self.assertEqual(len(res),5)
            self.assertTrue(all(bit in (0,1) for bit in res))

    def test_binary_add_commutativity(self):
        for _ in range(10):
            a = [random.randint(0,1) for _ in range(4)]
            b = [random.randint(0,1) for _ in range(4)]
            self.assertEqual(binary_add_4bit(a,b), binary_add_4bit(b,a))

    def test_binary_add_zero_identity(self):
        for _ in range(5):
            a = [random.randint(0,1) for _ in range(4)]
            self.assertEqual(binary_add_4bit(a,[0,0,0,0])[1:], a)
            self.assertEqual(binary_add_4bit([0,0,0,0],a)[1:], a)

    def test_binary_add_single_bit(self):
        for i in range(4):
            a = [0]*4
            a[i] = 1
            res = binary_add_4bit(a,[0,0,0,0])
            self.assertEqual(res[1:], a)

    def test_binary_add_carry_chain(self):
        a = [1,1,1,0]
        b = [0,1,1,1]
        # 1110 + 0111 = 10101
        self.check(a, b, [1,0,1,0,1])


class TestExtra(unittest.TestCase):
    def test_random_matrix_different(self):
        flat1 = create_binary_diagonal_matrix(5)
        flat2 = create_binary_diagonal_matrix(5)
        self.assertNotEqual(flat1, flat2)

    def test_random_matrix_repeatable(self):
        random.seed(99)
        flat1 = create_binary_diagonal_matrix(5)
        random.seed(99)
        flat2 = create_binary_diagonal_matrix(5)
        self.assertEqual(flat1, flat2)

    def test_get_word_full_range(self):
        N = 4
        flat = list(range(N*N))
        for col in range(N):
            w = get_word(flat, col, N)
            self.assertEqual(len(w), N)
            for i, bit in enumerate(w):
                self.assertEqual(bit, get_value(flat, (i+col)%N, col, N))


    def test_print_matrix_single(self):
        flat = [1]
        buf = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buf
        try:
            print_matrix(flat, 1)
        finally:
            sys.stdout = sys_stdout
        self.assertEqual(buf.getvalue().strip(), '1')

if __name__ == '__main__':
    unittest.main()
