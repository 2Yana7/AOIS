def f0(col: list) -> list:
    return [0] * len(col)

def f5(col: list) -> list:
    return col.copy()

def f10(col: list) -> list:
    return [1 - b for b in col]

def f15(col: list) -> list:
    return [1] * len(col)
