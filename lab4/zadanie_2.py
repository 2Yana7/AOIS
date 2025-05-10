# zadanie_2_fixed.py

def decimal_to_bcd8421(d):
    return [(d >> i) & 1 for i in reversed(range(4))]

def main():
    print(" d | D8421 | D8421+1")
    print("---+-------+--------")
    for d in range(10):
        bcd   = decimal_to_bcd8421(d)
        bcd1  = decimal_to_bcd8421(d + 1)
        print(f" {d} | {''.join(str(bit) for bit in bcd)} |  {''.join(str(bit) for bit in bcd1)}")


    forms = [
        "(X1 ∧ X2 ∧ X3) ∨ (X4 ∨ !X3)",
        "(X2 ∨ X3) ∧ (!X1 ∨ !X2 ∨ !X3) ∧ (X1 ∨ !X2 ∨ X3)",
        "(X1 ∧ X2) ∨ (!X1 ∧ X2)",
        "(!X1 ∧ !X2) ∨ (!X1 ∧ X2)"
    ]

    print("\nМинимальные формы для выходных битов (D8421+1):")
    for idx, expr in enumerate(forms):
        bit = 3 - idx
        kind = "КНФ" if idx == 1 else "ДНФ"
        print(f" c{bit} ({kind}): {expr}")

if __name__ == "__main__":
    main()
