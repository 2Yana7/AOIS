import re
import itertools
import math

class Node:
    def __init__(self, node_type, left=None, right=None, var=None):
        self.node_type = node_type
        self.left = left
        self.right = right
        self.var = var
        self.expr_str = None

def preprocess_expression(expr: str) -> str:
    return expr.replace(" ", "")

def tokenize(expr: str):
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i:i+2] == "->":
            tokens.append("->")
            i += 2
        elif expr[i] in ['(', ')', '!', '&', '|', '~']:
            tokens.append(expr[i])
            i += 1
        elif expr[i].isalpha():
            tokens.append(expr[i])
            i += 1
        else:
            i += 1
    return tokens

def shunting_yard(tokens):
    precedence = {'!': 4, '&': 3, '|': 2, '->': 1, '~': 0}
    right_assoc = {'!': True, '&': False, '|': False, '->': False, '~': False}
    output_queue = []
    op_stack = []
    for token in tokens:
        if token.isalpha():
            output_queue.append(token)
        elif token == '!':
            op_stack.append(token)
        elif token in ['&','|','->','~']:
            while op_stack and op_stack[-1] != '(':
                top = op_stack[-1]
                if top not in precedence:
                    break
                top_prec = precedence[top]
                cur_prec = precedence[token]
                if right_assoc.get(token, False):
                    if top_prec > cur_prec:
                        output_queue.append(op_stack.pop())
                    else:
                        break
                else:
                    if top_prec >= cur_prec:
                        output_queue.append(op_stack.pop())
                    else:
                        break
            op_stack.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            while op_stack and op_stack[-1] != '(':
                output_queue.append(op_stack.pop())
            if op_stack and op_stack[-1] == '(':
                op_stack.pop()
        else:
            raise ValueError(f"Неизвестный токен: {token}")
    while op_stack:
        output_queue.append(op_stack.pop())
    return output_queue

def rpn_to_ast(rpn_tokens):
    stack = []
    for token in rpn_tokens:
        if token.isalpha():
            stack.append(Node('var', var=token))
        elif token == '!':
            if not stack:
                raise ValueError("Ошибка: недостаточно операндов для '!'")
            operand = stack.pop()
            stack.append(Node('not', left=operand))
        elif token in ['&','|','->','~']:
            if len(stack) < 2:
                raise ValueError(f"Ошибка: недостаточно операндов для {token}")
            right = stack.pop()
            left = stack.pop()
            if token == '&':
                node_type = 'and'
            elif token == '|':
                node_type = 'or'
            elif token == '->':
                node_type = 'implies'
            elif token == '~':
                node_type = 'equiv'
            stack.append(Node(node_type, left=left, right=right))
        else:
            raise ValueError(f"Неизвестный токен в ОПЗ: {token}")
    if len(stack) != 1:
        raise ValueError("Ошибка: некорректное выражение (лишние операнды/операторы)")
    return stack[0]

def parse_expression(expr: str) -> Node:
    expr_prepared = preprocess_expression(expr)
    tokens = tokenize(expr_prepared)
    rpn = shunting_yard(tokens)
    ast = rpn_to_ast(rpn)
    return ast

def label_sub_expressions(root: Node) -> None:
    if root.node_type == 'var':
        root.expr_str = root.var
    elif root.node_type == 'not':
        label_sub_expressions(root.left)
        if root.left.node_type in ('and','or','implies','equiv'):
            root.expr_str = f"¬({root.left.expr_str})"
        else:
            root.expr_str = f"¬{root.left.expr_str}"
    elif root.node_type == 'and':
        label_sub_expressions(root.left)
        label_sub_expressions(root.right)
        left_s = root.left.expr_str
        right_s = root.right.expr_str
        if root.left.node_type in ('or','implies','equiv'):
            left_s = f"({left_s})"
        if root.right.node_type in ('or','implies','equiv'):
            right_s = f"({right_s})"
        root.expr_str = f"{left_s}∧{right_s}"
    elif root.node_type == 'or':
        label_sub_expressions(root.left)
        label_sub_expressions(root.right)
        left_s = root.left.expr_str
        right_s = root.right.expr_str
        if root.left.node_type in ('implies','equiv'):
            left_s = f"({left_s})"
        if root.right.node_type in ('and','implies','equiv'):
            right_s = f"({right_s})"
        root.expr_str = f"{left_s}∨{right_s}"
    elif root.node_type == 'implies':
        label_sub_expressions(root.left)
        label_sub_expressions(root.right)
        left_s = root.left.expr_str
        if root.left.node_type in ('and','or','implies','equiv'):
            left_s = f"({left_s})"
        right_s = root.right.expr_str
        if root.right.node_type in ('and','or','implies','equiv'):
            right_s = f"({right_s})"
        root.expr_str = f"{left_s}→{right_s}"
    elif root.node_type == 'equiv':
        label_sub_expressions(root.left)
        label_sub_expressions(root.right)
        left_s = root.left.expr_str
        if root.left.node_type in ('and','or','implies','equiv'):
            left_s = f"({left_s})"
        right_s = root.right.expr_str
        if root.right.node_type in ('and','or','implies','equiv'):
            right_s = f"({right_s})"
        root.expr_str = f"{left_s}↔{right_s}"

def compute_depth(node: Node) -> int:
    if node.node_type == 'var':
        return 1
    elif node.node_type == 'not':
        return compute_depth(node.left) + 1
    else:
        return max(compute_depth(node.left), compute_depth(node.right)) + 1

def collect_sub_expressions_in_order(root: Node):
    visited = {}
    result = []
    def traverse(node):
        if not node:
            return
        if node.node_type in ('and','or','implies','equiv'):
            traverse(node.left)
            if node.expr_str not in visited:
                visited[node.expr_str] = node
                result.append(node)
            traverse(node.right)
        elif node.node_type == 'not':
            traverse(node.left)
            if node.expr_str not in visited:
                visited[node.expr_str] = node
                result.append(node)
        else:
            if node.expr_str not in visited:
                visited[node.expr_str] = node
                result.append(node)
    traverse(root)
    return result

def evaluate_ast(root: Node, env: dict) -> bool:
    if root.node_type == 'var':
        return env[root.var]
    elif root.node_type == 'not':
        return not evaluate_ast(root.left, env)
    elif root.node_type == 'and':
        return evaluate_ast(root.left, env) and evaluate_ast(root.right, env)
    elif root.node_type == 'or':
        return evaluate_ast(root.left, env) or evaluate_ast(root.right, env)
    elif root.node_type == 'implies':
        return (not evaluate_ast(root.left, env)) or evaluate_ast(root.right, env)
    elif root.node_type == 'equiv':
        return evaluate_ast(root.left, env) == evaluate_ast(root.right, env)
    else:
        raise ValueError("Неизвестный тип узла")

def generate_truth_table_and_forms(expr: str):
    ast = parse_expression(expr)
    label_sub_expressions(ast)
    all_nodes = collect_sub_expressions_in_order(ast)
    var_nodes = [n for n in all_nodes if n.node_type == 'var']
    complex_nodes = [n for n in all_nodes if n.node_type != 'var']
    var_nodes_sorted = sorted(var_nodes, key=lambda n: n.var)
    if ast.node_type != 'var':
        non_root_complex = [n for n in complex_nodes if n is not ast]
        non_root_complex = sorted(non_root_complex, key=lambda n: compute_depth(n))
        columns = var_nodes_sorted + non_root_complex + [ast]
    else:
        columns = var_nodes_sorted
    header = " | ".join(node.expr_str for node in columns)
    print(header)
    print("-" * len(header))
    vars_sorted = [n.var for n in var_nodes_sorted]
    n_vars = len(vars_sorted)
    truth_rows = []
    index_bits = []
    for combo in itertools.product([0, 1], repeat=n_vars):
        env = {var: bool(val) for var, val in zip(vars_sorted, combo)}
        row_vals = []
        for node in columns:
            row_vals.append("1" if evaluate_ast(node, env) else "0")
        f_val = 1 if evaluate_ast(ast, env) else 0
        truth_rows.append((combo, f_val))
        index_bits.append("1" if f_val else "0")
        print(" | ".join(row_vals))
    minterms = []
    maxterms = []
    for combo, f_val in truth_rows:
        index = int("".join(str(bit) for bit in combo), 2)
        if f_val == 1:
            minterms.append(index)
        else:
            maxterms.append(index)
    dnf_terms = []
    cnf_terms = []
    for combo, f_val in truth_rows:
        if f_val == 1:
            term_literals = []
            for bit, var in zip(combo, vars_sorted):
                term_literals.append(var if bit == 1 else "¬" + var)
            dnf_terms.append("(" + "∧".join(term_literals) + ")")
        else:
            term_literals = []
            for bit, var in zip(combo, vars_sorted):
                term_literals.append(var if bit == 0 else "¬" + var)
            cnf_terms.append("(" + "∨".join(term_literals) + ")")
    dnf_formula = " ∨ ".join(dnf_terms)
    cnf_formula = " ∧ ".join(cnf_terms)
    binary_str = "".join(index_bits)
    index_value = int(binary_str, 2)
    binary_str_padded = format(index_value, f"0{2 ** n_vars}b")
    print("\nСовершенная дизъюнктивная нормальная форма (СДНФ)")
    print(dnf_formula)
    print("\nСовершенная конъюнктивная нормальная форма (СКНФ)")
    print(cnf_formula)
    print("\nЧисловые формы:")
    print("(" + ", ".join(str(i) for i in sorted(minterms)) + ") ∧")
    print("(" + ", ".join(str(i) for i in sorted(maxterms)) + ") ∨")
    print("\nИндексная форма")
    print(f"{index_value} - {binary_str_padded}")
    return {
        'minterms': sorted(minterms),
        'maxterms': sorted(maxterms),
        'dnf_formula': dnf_formula,
        'cnf_formula': cnf_formula,
        'index_value': index_value,
        'binary_str_padded': binary_str_padded,
        'vars_sorted': vars_sorted,
        'n_vars': n_vars,
        'ast': ast
    }

def group_to_term(group, grid, row_labels, col_labels, var_names, n_vars, for_dnf=True):
    (r1, c1), (r2, c2) = group
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    if n_vars == 1:
        cyclic_rows = False
        cyclic_cols = False
    elif n_vars == 2:
        cyclic_rows = False
        cyclic_cols = False
    elif n_vars == 3:
        cyclic_rows = False
        cyclic_cols = False
    elif n_vars in [4,5]:
        cyclic_rows = True
        cyclic_cols = True
    else:
        cyclic_rows = cyclic_cols = False
    cells = []
    def row_range(start, end):
        if start <= end:
            return range(start, end+1)
        else:
            return list(range(start, rows)) + list(range(0, end+1))
    def col_range(start, end):
        if start <= end:
            return range(start, end+1)
        else:
            return list(range(start, cols)) + list(range(0, end+1))
    row_iter = row_range(r1, (r2 % rows) if cyclic_rows else r2)
    col_iter = col_range(c1, (c2 % cols) if cyclic_cols else c2)
    for rr in row_iter:
        for cc in col_iter:
            cell = (rr % rows, cc % cols) if (cyclic_rows or cyclic_cols) else (rr, cc)
            if cell not in cells:
                cells.append(cell)
    bits_list = []
    for (r, c) in cells:
        if n_vars == 1:
            bits = row_labels[r].split('=')[1]
        elif n_vars == 2:
            row_bit = row_labels[r].split('=')[1]
            col_bit = col_labels[c].split('=')[1]
            bits = row_bit + col_bit
        elif n_vars == 3:
            row_bit = row_labels[r].split('=')[1]
            col_bits = col_labels[c].split('=')[1]
            bits = row_bit + col_bits
        elif n_vars in [4,5]:
            row_bits = row_labels[r].split('=')[1]
            col_bits = col_labels[c].split('=')[1]
            bits = row_bits + col_bits
        else:
            bits = ""
        bits_list.append(bits)
    if not bits_list:
        return "1" if for_dnf else "0"
    length = len(bits_list[0])
    term_bits = []
    for i in range(length):
        col_i_bits = [b[i] for b in bits_list]
        if all(bit == col_i_bits[0] for bit in col_i_bits):
            term_bits.append(col_i_bits[0])
        else:
            term_bits.append("X")
    res = []
    for i, b in enumerate(term_bits):
        if b == "X":
            continue
        v = var_names[i]
        if for_dnf:
            res.append(v if b == '1' else "¬" + v)
        else:
            res.append("¬" + v if b == '1' else v)
    connector = "∧" if for_dnf else "∨"
    return connector.join(res) if res else ("1" if for_dnf else "0")

def int_to_bin_str(num, n_vars):
    return format(num, '0{}b'.format(n_vars))

def combine_terms(t1, t2):
    diff = 0
    res = []
    for a, b in zip(t1, t2):
        if a == b:
            res.append(a)
        else:
            res.append('-')
            diff += 1
    return "".join(res) if diff == 1 else None

def bin_to_lits(bstr, vars_, is_dnf=True):
    res = []
    for ch, v in zip(bstr, vars_):
        if ch == '-':
            continue
        if is_dnf:
            res.append(v if ch == '1' else "¬" + v)
        else:
            res.append("¬" + v if ch == '1' else v)
    connector = "∧" if is_dnf else "∨"
    return connector.join(res) if res else ("1" if is_dnf else "0")

def literal_set_from_binary(bstr, vars_, is_dnf):
    lits = []
    for ch, v in zip(bstr, vars_):
        if ch == '-':
            continue
        if is_dnf:
            lits.append(v if ch == '1' else "¬" + v)
        else:
            lits.append("¬" + v if ch == '1' else v)
    return set(lits)

def covers(impl, bstr):
    return all(a == b or a == '-' for a, b in zip(impl, bstr))

def eliminate_redundant_implicants(implicants, terms, n_vars):
    reduced = list(implicants)
    changed = True
    while changed:
        changed = False
        for imp in list(reduced):
            test_set = [x for x in reduced if x != imp]
            all_covered = True
            for t in terms:
                b = int_to_bin_str(t, n_vars)
                if not any(covers(candidate, b) for candidate in test_set):
                    all_covered = False
                    break
            if all_covered:
                reduced.remove(imp)
                changed = True
    return reduced

def absorb_clauses(implicants, vars_, is_dnf):
    literal_sets = [(imp, literal_set_from_binary(imp, vars_, is_dnf)) for imp in implicants]
    result = []
    for i, (imp_i, set_i) in enumerate(literal_sets):
        redundant = False
        for j, (imp_j, set_j) in enumerate(literal_sets):
            if i != j and set_j <= set_i:
                redundant = True
                break
        if not redundant:
            result.append(imp_i)
    return result

def quine_mccluskey_calc(terms, n_vars, vars_, is_dnf=True):
    groups = {}
    for t in terms:
        b = int_to_bin_str(t, n_vars)
        ones = b.count('1')
        groups.setdefault(ones, set()).add(b)
    print("\n=== Склеивание: Исходные группы ===")
    for k in sorted(groups.keys()):
        items = sorted(groups[k])
        print(f"Группа {k}: " + ", ".join(bin_to_lits(x, vars_, is_dnf) for x in items))
    stage = 1
    final_combs = []
    while True:
        new_groups = {}
        combined_this_stage = set()
        sorted_keys = sorted(groups.keys())
        for i in range(len(sorted_keys) - 1):
            for term1 in groups[sorted_keys[i]]:
                for term2 in groups[sorted_keys[i+1]]:
                    comb = combine_terms(term1, term2)
                    if comb:
                        new_groups.setdefault(comb.count('1'), set()).add(comb)
                        combined_this_stage.add(term1)
                        combined_this_stage.add(term2)
        for k2 in groups:
            for t2 in groups[k2]:
                if t2 not in combined_this_stage:
                    final_combs.append(t2)
        if not new_groups:
            print(f"\n=== Склеивание завершено на стадии {stage} ===")
            break
        print(f"\n=== Стадия {stage} ===")
        for k3 in sorted(new_groups.keys()):
            items = sorted(new_groups[k3])
            print(f"Группа {k3}: " + ", ".join(bin_to_lits(x, vars_, is_dnf) for x in items))
        stage += 1
        groups = new_groups
    return sorted(set(final_combs))

def select_essential_calc(prime_implicants, terms, n_vars, vars_, is_dnf=True):
    if is_dnf:
        return prime_implicants
    else:
        remaining = list(prime_implicants)
        to_remove = set()
        for i in range(len(remaining)):
            for j in range(len(remaining)):
                if i != j:
                    set_i = literal_set_from_binary(remaining[i], vars_, is_dnf)
                    set_j = literal_set_from_binary(remaining[j], vars_, is_dnf)
                    if set_i <= set_j:
                        to_remove.add(remaining[j])
        return [imp for imp in remaining if imp not in to_remove]

def minimize_calc_dnf(minterms, n_vars, vars_):
    print("\n==== Минимизация СДНФ (расчётный метод) ====")
    prime = quine_mccluskey_calc(minterms, n_vars, vars_, is_dnf=True)
    need = select_essential_calc(prime, minterms, n_vars, vars_, is_dnf=True)
    need = eliminate_redundant_implicants(need, minterms, n_vars)
    result_terms = []
    for x in need:
        result_terms.append("(" + bin_to_lits(x, vars_, True) + ")")
    minimized = " ∨ ".join(result_terms)
    if minimized.strip() == "1":
        minimized = " ∨ ".join(vars_)
    print("\nРЕЗУЛЬТАТ (расчётный метод, СДНФ): " + minimized)
    return minimized

def minimize_calc_cnf(maxterms, n_vars, vars_):
    print("\n==== Минимизация СКНФ (расчётный метод) ====")
    prime = quine_mccluskey_calc(maxterms, n_vars, vars_, is_dnf=False)
    need = select_essential_calc(prime, maxterms, n_vars, vars_, is_dnf=False)
    need = eliminate_redundant_implicants(need, maxterms, n_vars)
    need = absorb_clauses(need, vars_, is_dnf=False)
    result_terms = []
    for x in need:
        result_terms.append("(" + bin_to_lits(x, vars_, False) + ")")
    minimized = " ∧ ".join(result_terms)
    print("\nРЕЗУЛЬТАТ (расчётный метод, СКНФ): " + minimized)
    return minimized

def build_table(prime, terms, n_vars, vars_, is_dnf=True):
    table = {}
    for p in prime:
        row = []
        for t in terms:
            b = int_to_bin_str(t, n_vars)
            row.append("Х" if covers(p, b) else ".")
        table[p] = row
    return table

def print_table_coverage(table, terms, vars_, is_dnf=True):
    header_cells = [term_to_clause(t, vars_, for_cnf=(not is_dnf)) for t in terms]
    header_cells = [cell.replace(" ", ".") for cell in header_cells]
    header = " " * 20 + " ".join(f"{cell:16}" for cell in header_cells)
    print("\nТаблица покрытия:")
    print(header)
    print("-" * len(header))
    for p in sorted(table.keys()):
        row_label = bin_to_lits(p, vars_, is_dnf)
        row = [cell if cell == "Х" else "." for cell in table[p]]
        print(f"{row_label:20} | " + " ".join(f"{cell:16}" for cell in row))

def term_to_clause(index, var_names, for_cnf=True):
    n = len(var_names)
    bits = format(index, f'0{n}b')
    literals = []
    for bit, v in zip(bits, var_names):
        if for_cnf:
            literal = ("¬" + v) if bit == '1' else v
        else:
            literal = v if bit == '1' else ("¬" + v)
        literals.append(literal)
    if for_cnf:
        return "(" + "∨".join(literals) + ")"
    else:
        return "(" + "∧".join(literals) + ")"

def quine_mccluskey_tabular(terms, n_vars, vars_, is_dnf=True):
    prime = quine_mccluskey_calc(terms, n_vars, vars_, is_dnf=is_dnf)
    coverage = build_table(prime, terms, n_vars, vars_, is_dnf=is_dnf)
    print_table_coverage(coverage, terms, vars_, is_dnf=is_dnf)
    return prime

def minimize_tab_dnf(minterms, n_vars, vars_):
    print("\n==== Минимизация СДНФ (расчётно-табличный метод) ====")
    prime = quine_mccluskey_tabular(minterms, n_vars, vars_, is_dnf=True)
    need = select_essential_calc(prime, minterms, n_vars, vars_, is_dnf=True)
    need = eliminate_redundant_implicants(need, minterms, n_vars)
    result = []
    for x in need:
        result.append("(" + bin_to_lits(x, vars_, True) + ")")
    minimized = " ∨ ".join(result)
    print("\nРЕЗУЛЬТАТ (табличный метод, СДНФ): " + minimized)
    return minimized

def minimize_tab_cnf(maxterms, n_vars, vars_):
    print("\n==== Минимизация СКНФ (расчётно-табличный метод) ====")
    prime = quine_mccluskey_tabular(maxterms, n_vars, vars_, is_dnf=False)
    need = select_essential_calc(prime, maxterms, n_vars, vars_, is_dnf=False)
    need = eliminate_redundant_implicants(need, maxterms, n_vars)
    need = absorb_clauses(need, vars_, is_dnf=False)
    result = []
    for x in need:
        result.append("(" + bin_to_lits(x, vars_, False) + ")")
    minimized = " ∧ ".join(result)
    print("\nРЕЗУЛЬТАТ (табличный метод, СКНФ): " + minimized)
    return minimized

def displayKMap(newGrid, newRowLabels, newColLabels):
    if newColLabels:
        print("         " + "  ".join(f"{lbl:12}" for lbl in newColLabels))
    for idx, newRow in enumerate(newGrid):
        if newRowLabels:
            print(f"{newRowLabels[idx]:12} " + "  ".join(f"{cell:12}" for cell in newRow))
        else:
            print("".join(str(cell) for cell in newRow))

def listRectangles(matrix, numVars=None):
    if numVars is None:
        numVars = 0
    numRows = len(matrix)
    numCols = len(matrix[0]) if numRows > 0 else 0
    isCyclicRows = numVars in [4,5]
    isCyclicCols = numVars in [4,5]
    rectList = []
    for startRow in range(numRows):
        for startCol in range(numCols):
            for dRow in range(numRows):
                for dCol in range(numCols):
                    endRow = startRow + dRow
                    endCol = startCol + dCol
                    if isCyclicRows:
                        endRow %= numRows
                    else:
                        if endRow >= numRows:
                            continue
                    if isCyclicCols:
                        endCol %= numCols
                    else:
                        if endCol >= numCols:
                            continue
                    if not isCyclicRows and endRow < startRow:
                        continue
                    if not isCyclicCols and endCol < startCol:
                        continue
                    area = (dRow + 1) * (dCol + 1)
                    if (area & (area - 1)) != 0:
                        continue
                    validRect = True
                    for r in range(startRow, startRow + dRow + 1):
                        for c in range(startCol, startCol + dCol + 1):
                            actualRow = r % numRows if isCyclicRows else r
                            actualCol = c % numCols if isCyclicCols else c
                            if actualRow >= numRows or actualCol >= numCols:
                                validRect = False
                                break
                            if matrix[actualRow][actualCol] != 1:
                                validRect = False
                                break
                        if not validRect:
                            break
                    if validRect:
                        rectList.append(((startRow, startCol), (endRow, endCol)))
    return rectList

def listZeroRectangles(matrix, numVars):
    numRows = len(matrix)
    numCols = len(matrix[0]) if numRows else 0
    if numVars == 3:
        isCyclicRows = False
        isCyclicCols = False
    else:
        isCyclicRows = numVars in [4,5]
        isCyclicCols = numVars in [4,5]
    rectList = []
    for rStart in range(numRows):
        for cStart in range(numCols):
            for dR in range(numRows):
                for dC in range(numCols):
                    rEnd = rStart + dR
                    cEnd = cStart + dC
                    if isCyclicRows:
                        rEnd %= numRows
                    else:
                        if rEnd >= numRows:
                            continue
                    if isCyclicCols:
                        cEnd %= numCols
                    else:
                        if cEnd >= numCols:
                            continue
                    if not isCyclicRows and rEnd < rStart:
                        continue
                    if not isCyclicCols and cEnd < cStart:
                        continue
                    area = (dR + 1) * (dC + 1)
                    if (area & (area - 1)) != 0:
                        continue
                    validRect = True
                    for r in range(rStart, rStart + dR + 1):
                        for c in range(cStart, cStart + dC + 1):
                            actualRow = r % numRows if isCyclicRows else r
                            actualCol = c % numCols if isCyclicCols else c
                            if matrix[actualRow][actualCol] != 0:
                                validRect = False
                                break
                        if not validRect:
                            break
                    if validRect:
                        rectList.append(((rStart, cStart), (rEnd, cEnd)))
    return rectList

def extractCells(rect, numVars, numRows, numCols):
    (sRow, sCol), (eRow, eCol) = rect
    if numVars == 3:
        isCyclicRows = False
        isCyclicCols = False
    else:
        isCyclicRows = numVars in [4,5]
        isCyclicCols = numVars in [4,5]
    cellSet = []
    def rowRange(st, ed, limit):
        if st <= ed:
            return range(st, ed+1)
        else:
            return list(range(st, limit)) + list(range(0, ed+1))
    def colRange(st, ed, limit):
        if st <= ed:
            return range(st, ed+1)
        else:
            return list(range(st, limit)) + list(range(0, ed+1))
    rRange = rowRange(sRow, (eRow % numRows) if isCyclicRows else eRow, numRows)
    cRange = colRange(sCol, (eCol % numCols) if isCyclicCols else eCol, numCols)
    for r in rRange:
        for c in cRange:
            cellSet.append((r % numRows, c % numCols) if (isCyclicRows or isCyclicCols) else (r, c))
    return set(cellSet)

def selectCover(groupCandidates, onesSet, numVars, numRows, numCols):
    selected = []
    remaining = set(onesSet)
    candidateCoverages = []
    for grp, termStr in groupCandidates:
        cells = extractCells(grp, numVars, numRows, numCols)
        candidateCoverages.append((cells, termStr))
    while remaining:
        bestChoice = None
        bestCov = 0
        for cells, termStr in candidateCoverages:
            coverageCount = len(remaining & cells)
            if coverageCount > bestCov:
                bestCov = coverageCount
                bestChoice = (cells, termStr)
        if bestChoice is None:
            break
        selected.append(bestChoice[1])
        remaining -= bestChoice[0]
    return selected

def selectZeroCover(groupCandidates, zerosSet, numVars, numRows, numCols):
    selected = []
    remaining = set(zerosSet)
    candidateCoverages = []
    for grp, termStr in groupCandidates:
        cells = extractCells(grp, numVars, numRows, numCols)
        candidateCoverages.append((cells, termStr))
    while remaining:
        bestChoice = None
        bestCov = 0
        for cells, termStr in candidateCoverages:
            coverageCount = len(remaining & cells)
            if coverageCount > bestCov:
                bestCov = coverageCount
                bestChoice = (cells, termStr)
        if bestChoice is None:
            break
        selected.append(bestChoice[1])
        remaining -= bestChoice[0]
    return selected

from itertools import combinations

from itertools import product

def gray_code(n):
    """Генерирует список Gray‑кодов длины n."""
    return [i ^ (i >> 1) for i in range(1 << n)]

def _to_binary_terms(terms, n_vars):
    return [tuple((t >> i) & 1 for i in reversed(range(n_vars))) for t in terms]

def _merge_pair(a, b):
    diff = 0
    merged = []
    for x, y in zip(a, b):
        if x != y:
            diff += 1
            merged.append('-')
        else:
            merged.append(x)
        if diff > 1:
            return None
    return tuple(merged) if diff == 1 else None

def _find_prime_implicants(terms, n_vars):
    groups = {}
    for t in terms:
        groups.setdefault(t.count(1), []).append(t)
    unchecked = set(terms)
    primes = set()
    while groups:
        new_groups = {}
        used = set()
        for i in sorted(groups):
            for t1 in groups[i]:
                for t2 in groups.get(i+1, []):
                    m = _merge_pair(t1, t2)
                    if m:
                        used |= {t1, t2}
                        new_groups.setdefault(m.count(1), []).append(m)
        primes |= (unchecked - used)
        unchecked = set(sum(new_groups.values(), []))
        groups = {}
        for t in unchecked:
            groups.setdefault(t.count(1), []).append(t)
    return primes

def _covers(pi, mt):
    return all(p == '-' or p == m for p, m in zip(pi, mt))

def _select_essential(primes, minterms):
    table = {pi: [mt for mt in minterms if _covers(pi, mt)] for pi in primes}
    essential = set()
    covered = set()
    for mt in minterms:
        cov = [pi for pi in primes if _covers(pi, mt)]
        if len(cov) == 1:
            essential.add(cov[0])
    for pi in essential:
        covered |= set(table[pi])
    rem = set(minterms) - covered
    while rem:
        pi, mts = max(table.items(), key=lambda kv: len(set(kv[1]) & rem))
        essential.add(pi)
        rem -= set(mts)
    return essential

def kmap_minimize(terms, n_vars, vars_, is_dnf=True):
    bits = _to_binary_terms(terms, n_vars)
    primes = _find_prime_implicants(bits, n_vars)
    essentials = _select_essential(primes, bits)
    sep = '∧' if is_dnf else '∨'
    out = []
    for pi in essentials:
        parts = []
        for name, b in zip(vars_, pi):
            if b == '-': continue
            if is_dnf:
                parts.append(name if b else f"¬{name}")
            else:
                parts.append(f"¬{name}" if b else name)
        out.append("(" + sep.join(parts) + ")")
    return out

def print_kmap_table(terms, n_vars, vars_, is_dnf=True):
    """
    Печатает ASCII-карту Карно с подписями переменных.
    """
    r = n_vars // 2
    c = n_vars - r
    row_codes = gray_code(r)
    col_codes = gray_code(c)
    term_set = set(terms)

    row_vars = "".join(vars_[:r])
    col_vars = "".join(vars_[r:])

    # Заголовок
    print(f"{row_vars:>{r}} \\ {col_vars:<{c}}", end=" | ")
    for code in col_codes:
        print(f"{code:0{c}b}", end=" | ")
    print()
    print("-" * ((c + 3) * (len(col_codes) + 1)))

    # Строки таблицы
    for rc in row_codes:
        row_bits = f"{rc:0{r}b}"
        print(f"{row_bits:>{r}}{' ' * (3 - r)}", end=" | ")
        for cc in col_codes:
            col_bits = f"{cc:0{c}b}"
            full = row_bits + col_bits
            idx = int(full, 2)
            val = 1 if is_dnf else 0
            cell = str(val) if idx in term_set else str(1 - val)
            print(f" {cell} ", end="|")
        print()


# --- Пример вызова ---

def main():
    expr = input("Введите логическое выражение :\n")
    print("\nТаблица истинности с подвыражениями:\n")
    data = generate_truth_table_and_forms(expr)
    minterms = data['minterms']
    maxterms = data['maxterms']
    n_vars = data['n_vars']
    vars_ = data['vars_sorted']
    print("\n========== Результаты минимизации ==========")
    dnf_calc = minimize_calc_dnf(minterms, n_vars, vars_)
    cnf_calc = minimize_calc_cnf(maxterms, n_vars, vars_)
    dnf_tab = minimize_tab_dnf(minterms, n_vars, vars_)
    cnf_tab = minimize_tab_cnf(maxterms, n_vars, vars_)
    dnf_kmap = kmap_minimize(minterms, n_vars, vars_, is_dnf=True)
    cnf_kmap = kmap_minimize(maxterms, n_vars, vars_, is_dnf=False)

    print("Карта для DNF (1→единицы):")
    print_kmap_table(minterms, n_vars, vars_, is_dnf=True)
    print("\nКарта для CNF (0→нули):")
    print_kmap_table(maxterms, n_vars, vars_, is_dnf=False)

    print("\n======= Итоговый рез =======")

    print("\nРезультаты минимизации для СДНФ:")
    print("  1) Расчетный метод (Куайн–МакКласки):", dnf_calc)
    print("  2) Расчетно-табличный метод:         ", dnf_tab)
    print("  3) Метод Карно:                      ",  " ∨ ".join(dnf_kmap))
    print("\nРезультаты минимизации для СКНФ:")
    print("  1) Расчетный метод (Куайн–МакКласки):", cnf_calc)
    print("  2) Расчетно-табличный метод:         ", cnf_tab)
    print("  3) Метод Карно:                      ", " ∧ ".join(cnf_kmap))


if __name__ == "__main__":
    main()
