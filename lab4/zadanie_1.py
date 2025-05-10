import re
import itertools
import math

vars = ['X1', 'X2', 'X3']
rows = [
    (0,0,0, 0,0),
    (0,0,1, 0,1),
    (0,1,0, 0,1),
    (0,1,1, 1,0),
    (1,0,0, 0,1),
    (1,0,1, 1,0),
    (1,1,0, 1,0),
    (1,1,1, 1,1),
]

def to_bin(n, width):
    return format(n, f'0{width}b')

def count_bits(s, ch):
    return len(re.findall(ch, s))

def combine_terms(a, b):
    diff = 0
    out = []
    for ca, cb in zip(a, b):
        if ca == cb:
            out.append(ca)
        else:
            diff += 1
            out.append('-')
            if diff > 1:
                return None
    return ''.join(out)

def find_prime_implicants(minterms, num_vars):

    groups = {}
    for m in minterms:
        b = to_bin(m, num_vars)
        cnt = count_bits(b, '1')
        groups.setdefault(cnt, set()).add(b)
    primes = set()
    while groups:
        new_groups = {}
        used = set()
        for i in sorted(groups):
            if i+1 not in groups:
                continue
            for a, b in itertools.product(groups[i], groups[i+1]):
                c = combine_terms(a, b)
                if c:
                    used.add(a); used.add(b)
                    k = count_bits(c, '1')
                    new_groups.setdefault(k, set()).add(c)
        for grp in groups.values():
            for term in grp:
                if term not in used:
                    primes.add(term)
        groups = new_groups
    return primes

def covers(imp, m, num_vars):
    b = to_bin(m, num_vars)
    return all(ic=='-' or ic==bc for ic, bc in zip(imp, b))

def select_essential(primes, minterms):
    chart = {imp: {m for m in minterms if covers(imp, m, num_vars)}
             for imp in primes}
    inv = {}
    for imp, cov in chart.items():
        for m in cov:
            inv.setdefault(m, []).append(imp)
    solution = set()
    covered = set()
    for m, imps in inv.items():
        if len(imps) == 1:
            solution.add(imps[0])
            covered |= chart[imps[0]]
    remaining = set(minterms) - covered
    while remaining:
        best = max(chart, key=lambda imp: len(chart[imp] & remaining))
        solution.add(best)
        covered |= chart[best]
        remaining = set(minterms) - covered
    return solution

def implicant_to_clause(imp):
    lits = []
    for bit, name in zip(imp, vars):
        if bit == '1':
            lits.append(name)
        elif bit == '0':
            lits.append(f"¬{name}")
    return "(" + "  ∨  ".join(lits) + ")"

def minimize_dnf(minterms, num_vars):
    if not minterms:
        return "0"
    primes = find_prime_implicants(minterms, num_vars)
    essentials = select_essential(primes, minterms)
    clauses = [implicant_to_clause(imp) for imp in sorted(essentials)]
    return " ∧ ".join(clauses)

num_vars = int(math.log2(len(rows)))

minterms_P = []
minterms_D = []
for x1, x2, x3, p, d in rows:
    idx = (x1 << 2) | (x2 << 1) | x3
    if p: minterms_P.append(idx)
    if d: minterms_D.append(idx)

print(f"{'X1':>2} {'X2':>2} {'X3':>2} {'Bi+1':>4} {'D':>2}")
print('-' * 17)
for x1, x2, x3, p, d in rows:
    print(f"{x1:>2} {x2:>2} {x3:>2} {p:>4} {d:>2}")

dnf_P = minimize_dnf(minterms_P, num_vars)
dnf_D = minimize_dnf(minterms_D, num_vars)

print("\nМинимизированная КНФ:")
print("Bi+1 =", dnf_P)
print("D    =", dnf_D)
