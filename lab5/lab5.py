tt_lines = [
    "0   0   0  | 0 |  0  0  0 |  0  0  0",
    "0   0   0  | 1 |  1  1  1 |  1  1  1",
    "0   0   1  | 0 |  0  0  1 |  0  0  0",
    "0   0   1  | 1 |  0  0  0 |  0  0  1",
    "0   1   0  | 0 |  0  1  0 |  0  0  0",
    "0   1   0  | 1 |  0  0  1 |  0  1  1",
    "0   1   1  | 0 |  0  1  1 |  0  0  0",
    "0   1   1  | 1 |  0  1  0 |  0  0  1",
    "1   0   0  | 0 |  1  0  0 |  0  0  0",
    "1   0   0  | 1 |  0  1  1 |  1  1  1",
    "1   0   1  | 0 |  1  0  1 |  0  0  0",
    "1   0   1  | 1 |  1  0  0 |  0  0  1",
    "1   1   0  | 0 |  1  1  0 |  0  0  0",
    "1   1   0  | 1 |  1  0  1 |  0  1  1",
    "1   1   1  | 0 |  1  1  1 |  0  0  0",
    "1   1   1  | 1 |  1  1  0 |  0  0  1",
]

def print_truth_table():
    print(" q3* q2* q1* | V | q1 q2 q3 | h3 h2 h1")
    print("----------------------------------------")
    for line in tt_lines:
        print(line)

def minimize_dnf_h():
    
    mn = {
        'h3': '!q2 /\\ !q1 /\\ V',
        'h2': '!q1 /\\ V',
        'h1': 'V'
    }
    return mn

def print_min_dnf():
    mn = minimize_dnf_h()
    print("\nМинимизированные DNF для выходов:")
    print(f"h3 : {mn['h3']}")
    print(f"h2 : {mn['h2']}")
    print(f"h1 : {mn['h1']}")

if __name__ == "__main__":
    print_truth_table()
    print_min_dnf()
