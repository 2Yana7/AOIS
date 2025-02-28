import io
import unittest
from contextlib import redirect_stdout
import builtins

from lab_1_3 import (
    int_to_bin, bin_to_int, decimal_to_binary, decimal_to_ones_complement,
    decimal_to_twos_complement, binary_addition, binary_subtraction,
    binary_multiplication, binary_division, float_to_ieee754, ieee754_to_float,
    add_ieee754, main
)

class TestBinaryConversions(unittest.TestCase):
    def test_int_to_bin(self):
        self.assertEqual(int_to_bin(5, 8), '00000101')
        self.assertEqual(int_to_bin(0, 4), '0000')
        self.assertEqual(int_to_bin(15, 4), '1111')
        self.assertEqual(int_to_bin(16, 5), '10000')

    def test_bin_to_int(self):
        self.assertEqual(bin_to_int('00000101'), 5)
        self.assertEqual(bin_to_int('1111'), 15)
        self.assertEqual(bin_to_int('0'), 0)
        self.assertEqual(bin_to_int('1010'), 10)

class TestDecimalCodes(unittest.TestCase):
    def test_decimal_to_binary(self):
        self.assertEqual(decimal_to_binary(5, 8), '00000101')
        self.assertEqual(decimal_to_binary(-5, 8), '10000101')
        self.assertEqual(decimal_to_binary(0, 8), '00000000')

    def test_decimal_to_ones_complement(self):
        self.assertEqual(decimal_to_ones_complement(3, 4), '0011')
        self.assertEqual(decimal_to_ones_complement(-3, 4), '1100')
        self.assertEqual(decimal_to_ones_complement(0, 8), '00000000')

    def test_decimal_to_twos_complement(self):
        self.assertEqual(decimal_to_twos_complement(3, 4), '0011')
        self.assertEqual(decimal_to_twos_complement(-3, 4), '1101')
        self.assertEqual(decimal_to_twos_complement(0, 8), '00000000')

class TestBinaryOperations(unittest.TestCase):
    def test_binary_addition(self):
        self.assertEqual(binary_addition(127, 1, 8), -128)
        self.assertEqual(binary_addition(5, 3, 8), 8)
        self.assertEqual(binary_addition(-5, -3, 8), -8)

    def test_binary_subtraction(self):
        self.assertEqual(binary_subtraction(5, 3, 8), 2)
        self.assertEqual(binary_subtraction(3, 5, 8), -2)
        self.assertEqual(binary_subtraction(-5, -3, 8), -2)

    def test_binary_multiplication(self):
        self.assertEqual(binary_multiplication('00000011', '00000010', 8), '00000110')
        self.assertEqual(binary_multiplication('10000011', '00000010', 8), '10000110')
        self.assertEqual(binary_multiplication('00000011', '10000010', 8), '10000110')

    def test_binary_division(self):
        self.assertEqual(binary_division('00000110', '00000011', 8, 5)[1], 2.0)
        self.assertEqual(binary_division('00000101', '00000010', 8, 5)[1], 2.5)
        self.assertEqual(binary_division('00000000', '00000001', 8, 5)[1], 0.0)
        self.assertEqual(binary_division('00000001', '00000000', 8, 5)[0], "Ошибка: деление на ноль")

class TestIEEE754Conversions(unittest.TestCase):
    def test_float_to_ieee754(self):
        self.assertEqual(float_to_ieee754(0.0), '0' * 32)
        self.assertEqual(float_to_ieee754(1.0), '00111111100000000000000000000000')
        self.assertEqual(float_to_ieee754(-1.0), '10111111100000000000000000000000')

    def test_ieee754_to_float(self):
        self.assertEqual(ieee754_to_float('0' * 32), 0.0)
        self.assertAlmostEqual(ieee754_to_float('00111111100000000000000000000000'), 1.0)
        self.assertAlmostEqual(ieee754_to_float('10111111100000000000000000000000'), -1.0)

    def test_add_ieee754(self):
        self.assertEqual(add_ieee754(1.0, 2.0), float_to_ieee754(3.0))
        self.assertEqual(add_ieee754(-1.0, 1.0), float_to_ieee754(0.0))

class TestMainFunction(unittest.TestCase):
    def test_main_integer(self):
        """
        Тест для интерактивного режима для целых чисел.
        Эмулируем ввод: выбор режима "1", затем два числа.
        """
        input_values = ["1", "5", "3"]
        def fake_input(prompt):
            return input_values.pop(0)
        original_input = builtins.input
        builtins.input = fake_input

        try:
            f = io.StringIO()
            with redirect_stdout(f):
                main()
            output = f.getvalue()
            # Проверяем, что в выводе присутствуют ключевые надписи для целых чисел.
            self.assertIn("[Прямой код]", output)
            self.assertIn("[Обратный код]", output)
            self.assertIn("[Дополнительный код]", output)
            self.assertIn("[Сложение]", output)
            self.assertIn("[Вычитание]", output)
            self.assertIn("[Умножение]", output)
            self.assertIn("[Деление]", output)
        finally:
            builtins.input = original_input

    def test_main_float(self):
        """
        Тест для интерактивного режима для чисел с плавающей точкой.
        Эмулируем ввод: выбор режима "2", затем два числа.
        """
        input_values = ["2", "1.0", "2.0"]
        def fake_input(prompt):
            return input_values.pop(0)
        original_input = builtins.input
        builtins.input = fake_input

        try:
            f = io.StringIO()
            with redirect_stdout(f):
                main()
            output = f.getvalue()
            # Проверяем, что в выводе присутствуют ключевые надписи для формата IEEE-754.
            self.assertIn("[IEEE-754 32-bit]", output)
            self.assertIn("Первое число:", output)
            self.assertIn("Второе число:", output)
            self.assertIn("[Сложение]", output)
        finally:
            builtins.input = original_input

if __name__ == '__main__':
    unittest.main()
