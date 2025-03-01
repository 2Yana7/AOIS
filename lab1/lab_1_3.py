# для операций с фиксированной точкой (деление)
INTEGER_BITS = 8
FRACTIONAL_BITS = 5

# для формата IEEE-754 (32-бит, одинарная точность)
IEEE754_TOTAL_BITS = 32
IEEE754_SIGN_BITS = 1
IEEE754_EXPONENT_BITS = 8
IEEE754_MANTISSA_BITS = 23
IEEE754_BIAS = 127

"""из 10-того в 2-ый код"""


def int_to_bin(n: int, bits: int) -> str:
    result = ""
    for i in range(bits - 1, -1, -1):
        if n >= (1 << i):
            result += "1"
            n -= (1 << i)
        else:
            result += "0"
    return result


"""из 2-ного в 10-ный код"""


def bin_to_int(bin_str: str) -> int:
    result = 0
    for digit in bin_str:
        result = result * 2 + (1 if digit == "1" else 0)
    return result


"""из десятичного формата в двоичный в прямом коде"""


def decimal_to_binary(n: int, bits: int) -> str:
    if n >= 0:
        return int_to_bin(n, bits)
    else:
        return "1" + int_to_bin(abs(n), bits - 1)


"""из десятичного формата в двоичный в обратном (единичном) коде"""


def decimal_to_ones_complement(n: int, bits: int) -> str:
    if n >= 0:
        return int_to_bin(n, bits)
    else:
        magnitude_bin = int_to_bin(abs(n), bits - 1)
        inverted = "".join("0" if bit == "1" else "1" for bit in magnitude_bin)
        return "1" + inverted


"""Переводит число n из десятичного формата в двоичный в дополнительном коде."""


def decimal_to_twos_complement(n: int, bits: int) -> str:
    if n >= 0:
        return int_to_bin(n, bits)
    else:
        value = (1 << bits) - abs(n)
        return int_to_bin(value, bits)


"""Складывает два целых числа в дополнительном коде"""


def binary_addition(a: int, b: int, bits: int) -> int:
    max_val = 1 << bits
    result = (a + b) % max_val
    if result >= (1 << (bits - 1)):
        result -= (1 << bits)
    return result


"""Вычитает b из a в дополнительном коде."""


def binary_subtraction(a: int, b: int, bits: int) -> int:
    return binary_addition(a, -b, bits)


"""Умножает два числа"""


def binary_multiplication(a_bin: str, b_bin: str, bits: int) -> str:
    # Определяем знак результата
    sign = "1" if a_bin[0] != b_bin[0] else "0"

    # Работаем с абсолютными значениями
    a_abs = bin_to_int(a_bin[1:])
    b_abs = bin_to_int(b_bin[1:])

    # Выполняем умножение
    product = a_abs * b_abs

    # Ограничиваем результат количеством бит (исключая знаковый бит)
    max_val = 1 << (bits - 1)
    if product >= max_val:
        product = product % max_val  # Обрезаем переполнение

    # Преобразуем результат в двоичный формат
    binary_product = int_to_bin(product, bits - 1)

    # Возвращаем результат с учетом знака
    return sign + binary_product


"""Выполняет деление двух чисел"""


def binary_division(a_bin: str, b_bin: str, integer_bits=INTEGER_BITS, fractional_bits=FRACTIONAL_BITS) -> tuple:
    b_abs = bin_to_int(b_bin[1:])
    if b_abs == 0:
        return ("Ошибка: деление на ноль", "Ошибка: деление на ноль")
    sign = "1" if a_bin[0] != b_bin[0] else "0"
    a_abs = bin_to_int(a_bin[1:])
    b_abs = bin_to_int(b_bin[1:])
    quotient_int = a_abs // b_abs
    remainder = a_abs % b_abs
    fractional = []
    for _ in range(fractional_bits):
        remainder *= 2
        if remainder >= b_abs:
            fractional.append("1")
            remainder -= b_abs
        else:
            fractional.append("0")
    binary_int = int_to_bin(quotient_int, integer_bits)
    binary_frac = "".join(fractional)
    result_binary = f"{sign} {binary_int} {binary_frac}"
    decimal_result = quotient_int
    for i, bit in enumerate(fractional):
        if bit == "1":
            decimal_result += 2 ** (-(i + 1))
    if sign == "1":
        decimal_result = -decimal_result
    return (result_binary, decimal_result)


"""Преобразует число num из десятичного формата в 32-битный формат IEEE-754"""


def float_to_ieee754(num: float) -> str:
    if num == 0:
        return "0" * IEEE754_TOTAL_BITS
    sign_bit = "0"
    if num < 0:
        sign_bit = "1"
        num = -num
    e = 0
    temp = num
    while temp >= 2:
        temp /= 2
        e += 1
    while temp < 1:
        temp *= 2
        e -= 1
    exponent = e + IEEE754_BIAS
    fraction = temp - 1
    mantissa = int(round(fraction * (1 << IEEE754_MANTISSA_BITS)))
    if mantissa == (1 << IEEE754_MANTISSA_BITS):
        exponent += 1
        mantissa = 0
    exponent_bin = int_to_bin(exponent, IEEE754_EXPONENT_BITS)
    mantissa_bin = int_to_bin(mantissa, IEEE754_MANTISSA_BITS)
    return sign_bit + exponent_bin + mantissa_bin


"""Преобразует 32-битное представление числа в формате IEEE-754 в десятичное число"""


def ieee754_to_float(binary: str) -> float:
    if len(binary) != IEEE754_TOTAL_BITS:
        return None
    sign_bit = binary[0]
    exponent_bin = binary[1:1 + IEEE754_EXPONENT_BITS]
    mantissa_bin = binary[1 + IEEE754_EXPONENT_BITS:]
    exponent = 0
    for digit in exponent_bin:
        exponent = exponent * 2 + (1 if digit == "1" else 0)
    mantissa = 0
    for digit in mantissa_bin:
        mantissa = mantissa * 2 + (1 if digit == "1" else 0)
    if exponent == 0:
        value = mantissa / (1 << IEEE754_MANTISSA_BITS)
        result = value * (2 ** (1 - IEEE754_BIAS))
    else:
        e = exponent - IEEE754_BIAS
        value = 1 + mantissa / (1 << IEEE754_MANTISSA_BITS)
        result = value * (2 ** e)
    if sign_bit == "1":
        result = -result
    return result


"""Складывает два числа в формате IEEE-754"""


def add_ieee754(num1: float, num2: float) -> str:
    result = num1 + num2
    return float_to_ieee754(result)


def calculate_required_bits(n: int) -> int:
    """Вычисляет необходимое количество бит для представления числа n."""
    if n == 0:
        return 1
    return n.bit_length() + 1  # +1 для знакового бита


def main():
    print("Выберите тип чисел:")
    print("1 - Целые числа")
    print("2 - Числа с плавающей точкой")
    choice = input("Ваш выбор: ")

    if choice == '2':
        num1 = float(input("Введите первое число (десятичное): "))
        num2 = float(input("Введите второе число (десятичное): "))

        a_bin = float_to_ieee754(num1)
        b_bin = float_to_ieee754(num2)
        sum_bin = add_ieee754(num1, num2)
        sum_float = ieee754_to_float(sum_bin)

        print("\n[IEEE-754 32-bit]")
        print(f"Первое число: {a_bin}")
        print(f"Второе число: {b_bin}")
        print(f"\n[Сложение] {sum_bin} (десятичное: {sum_float})")

    else:
        num1 = int(input("Введите первое число (десятичное): "))
        num2 = int(input("Введите второе число (десятичное): "))

        # Вычисляем необходимое количество бит
        bits = max(calculate_required_bits(num1), calculate_required_bits(num2))

        a_bin = decimal_to_binary(num1, bits)
        b_bin = decimal_to_binary(num2, bits)

        print(f"\n[Прямой код]")
        print(f"Первое число: {a_bin}")
        print(f"Второе число: {b_bin}")

        print(f"\n[Обратный код]")
        print(f"Первое число: {decimal_to_ones_complement(num1, bits)}")
        print(f"Второе число: {decimal_to_ones_complement(num2, bits)}")

        print(f"\n[Дополнительный код]")
        print(f"Первое число: {decimal_to_twos_complement(num1, bits)}")
        print(f"Второе число: {decimal_to_twos_complement(num2, bits)}")

        sum_result = binary_addition(num1, num2, bits)
        sub_result = binary_subtraction(num1, num2, bits)
        print(f"\n[Сложение] {decimal_to_twos_complement(sum_result, bits)} (десятичное: {sum_result})")
        print(f"[Вычитание] {decimal_to_twos_complement(sub_result, bits)} (десятичное: {sub_result})")

        # Умножение
        bits_mult = calculate_required_bits(num1) + calculate_required_bits(num2)
        product_bin = binary_multiplication(a_bin, b_bin, bits_mult)
        product_decimal = (-1 if product_bin[0] == "1" else 1) * bin_to_int(product_bin[1:])
        print(f"\n[Умножение] {product_bin} (десятичное: {product_decimal})")

        # Деление
        if bin_to_int(b_bin[1:]) == 0:
            print("\n[Деление] Ошибка: деление на ноль")
        else:
            division_bin, division_dec = binary_division(a_bin, b_bin)
            print(f"\n[Деление]")
            print(f"Двоичный: {division_bin}")
            print(f"Десятичный: {division_dec:.5f}")


if __name__ == "__main__":
    main()