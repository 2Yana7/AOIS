def binary_add_4bit(a: list, b: list) -> list:
    carry = 0
    result = [0] * 5
    for idx in range(3, -1, -1):
        total = a[idx] + b[idx] + carry
        result[idx + 1] = total % 2
        carry = total // 2
    result[0] = carry
    return result
