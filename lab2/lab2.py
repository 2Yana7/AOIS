import re
import itertools


# ------------------ Узел дерева ------------------ #
class Node:
    """
    Узел дерева разбора.
    node_type: 'var', 'not', 'and', 'or', 'implies', 'equiv'
    left, right: дочерние узлы (для not: right=None)
    var: имя переменной (если node_type == 'var')
    expr_str: строковое представление подвыражения (будет сформировано позже)
    """
    def __init__(self, node_type, left=None, right=None, var=None):
        self.node_type = node_type
        self.left = left
        self.right = right
        self.var = var
        self.expr_str = None


# ------------------ Шаг 1. Предобработка выражения ------------------ #
def preprocess_expression(expr: str) -> str:
    """
    Убирает пробелы. Импликация обрабатывается как отдельный оператор.
    """
    return expr.replace(" ", "")


# ------------------ Шаг 2. Токенизация ------------------ #
def tokenize(expr: str):
    """
    Преобразует строку в список токенов:
      - многосимвольный оператор "->"
      - скобки, операторы !, &, |, ~
      - переменные: a, b, c, d, e.
    Символ "~" здесь трактуется как оператор эквиваленции.
    """
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i:i + 2] == "->":
            tokens.append("->")
            i += 2
        elif expr[i] in ['(', ')', '!', '&', '|', '~']:
            tokens.append(expr[i])
            i += 1
        elif expr[i] in ['a', 'b', 'c', 'd', 'e']:
            tokens.append(expr[i])
            i += 1
        else:
            # Игнорируем неизвестные символы
            i += 1
    return tokens


# ------------------ Шаг 3. Сортировочная станция ------------------ #
def shunting_yard(tokens):
    """
    Преобразует список токенов в обратную польскую запись (ОПЗ).
    Приоритеты (чем больше число – тем выше приоритет):
      !       – 4 (унарный, правая ассоциативность)
      &       – 3
      |       – 2
      ->      – 1 (правоассоциативный)
      ~       – 0 (левоассоциативный, самый низкий приоритет)
    """
    precedence = {'!': 4, '&': 3, '|': 2, '->': 1, '~': 0}
    right_assoc = {'!': True, '&': False, '|': False, '->': True, '~': False}

    output_queue = []
    op_stack = []

    for token in tokens:
        if token in ['a', 'b', 'c', 'd', 'e']:
            output_queue.append(token)
        elif token == '!':
            op_stack.append(token)
        elif token in ['&', '|', '->', '~']:
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


# ------------------ Шаг 4. Построение AST (дерева) ------------------ #
def rpn_to_ast(rpn_tokens):
    """
    По списку токенов в ОПЗ строим AST.
    Для унарного оператора '!' берем один операнд,
    для бинарных операторов (&, |, ->, ~) – два.
    """
    stack = []
    for token in rpn_tokens:
        if token in ['a', 'b', 'c', 'd', 'e']:
            stack.append(Node('var', var=token))
        elif token == '!':
            if not stack:
                raise ValueError("Ошибка: недостаточно операндов для '!'")
            operand = stack.pop()
            stack.append(Node('not', left=operand))
        elif token in ['&', '|', '->', '~']:
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
    """
    Полный цикл: предобработка, токенизация, сортировочная станция, построение AST.
    """
    expr_prepared = preprocess_expression(expr)
    tokens = tokenize(expr_prepared)
    rpn = shunting_yard(tokens)
    ast = rpn_to_ast(rpn)
    return ast


# ------------------ Шаг 5. Формирование строк подвыражений ------------------ #
def label_sub_expressions(root: Node) -> None:
    if root.node_type == 'var':
        root.expr_str = root.var
    elif root.node_type == 'not':
        label_sub_expressions(root.left)
        if root.left.node_type in ('and', 'or', 'implies', 'equiv'):
            root.expr_str = f"¬({root.left.expr_str})"
        else:
            root.expr_str = f"¬{root.left.expr_str}"
    elif root.node_type == 'and':
        label_sub_expressions(root.left)
        label_sub_expressions(root.right)
        left_s = root.left.expr_str
        right_s = root.right.expr_str
        if root.left.node_type in ('or', 'implies', 'equiv'):
            left_s = f"({left_s})"
        if root.right.node_type in ('or', 'implies', 'equiv'):
            right_s = f"({right_s})"
        root.expr_str = f"{left_s}∧{right_s}"
    elif root.node_type == 'or':
        label_sub_expressions(root.left)
        label_sub_expressions(root.right)
        left_s = root.left.expr_str
        right_s = root.right.expr_str
        if root.left.node_type in ('implies', 'equiv'):
            left_s = f"({left_s})"
        if root.right.node_type in ('and', 'implies', 'equiv'):
            right_s = f"({right_s})"
        root.expr_str = f"{left_s}∨{right_s}"
    elif root.node_type == 'implies':
        label_sub_expressions(root.left)
        label_sub_expressions(root.right)
        left_s = root.left.expr_str
        if root.left.node_type in ('and', 'or', 'implies', 'equiv'):
            left_s = f"({left_s})"
        right_s = root.right.expr_str
        if root.right.node_type in ('and', 'or', 'implies', 'equiv'):
            right_s = f"({right_s})"
        root.expr_str = f"{left_s}→{right_s}"
    elif root.node_type == 'equiv':
        label_sub_expressions(root.left)
        label_sub_expressions(root.right)
        left_s = root.left.expr_str
        if root.left.node_type in ('and', 'or', 'implies', 'equiv'):
            left_s = f"({left_s})"
        right_s = root.right.expr_str
        if root.right.node_type in ('and', 'or', 'implies', 'equiv'):
            right_s = f"({right_s})"
        root.expr_str = f"{left_s}↔{right_s}"


# ------------------ Дополнительно: вычисление глубины узла ------------------ #
def compute_depth(node: Node) -> int:
    """
    Рекурсивно вычисляет глубину узла (глубина переменной = 1, для бинарных узлов – max глубины детей + 1).
    """
    if node.node_type == 'var':
        return 1
    elif node.node_type == 'not':
        return compute_depth(node.left) + 1
    else:
        return max(compute_depth(node.left), compute_depth(node.right)) + 1


# ------------------ Шаг 6. Сбор подвыражений для таблицы ------------------ #
def collect_sub_expressions_in_order(root: Node):
    """
    Возвращает список узлов (Node) без повторений.
    Для формирования столбцов таблицы:
      – переменные (узлы с типом 'var') собираются отдельно и сортируются по алфавиту,
      – комплексные подвыражения сортируются по их глубине (от простых к более сложным),
      – полный вид (корневой узел) выводится в последнюю колонку.
    """
    visited = {}
    result = []

    def traverse(node):
        if not node:
            return
        if node.node_type in ('and', 'or', 'implies', 'equiv'):
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
        else:  # var
            if node.expr_str not in visited:
                visited[node.expr_str] = node
                result.append(node)

    traverse(root)
    return result


# ------------------ Шаг 7. Вычисление значения выражения ------------------ #
def evaluate_ast(root: Node, env: dict) -> bool:
    """
    Рекурсивно вычисляет значение выражения (AST) при заданном окружении env (словарь переменных).
    """
    if root.node_type == 'var':
        return env[root.var]
    elif root.node_type == 'not':
        return not evaluate_ast(root.left, env)
    elif root.node_type == 'and':
        return evaluate_ast(root.left, env) and evaluate_ast(root.right, env)
    elif root.node_type == 'or':
        return evaluate_ast(root.left, env) or evaluate_ast(root.right, env)
    elif root.node_type == 'implies':
        # Импликация: A→B эквивалентно ¬A ∨ B
        return (not evaluate_ast(root.left, env)) or evaluate_ast(root.right, env)
    elif root.node_type == 'equiv':
        # Эквиваленция: A↔B истинна, когда A и B имеют одинаковые значения
        return evaluate_ast(root.left, env) == evaluate_ast(root.right, env)
    else:
        raise ValueError("Неизвестный тип узла")


# ------------------ Шаг 8. Генерация таблицы истинности и вычисление форм ------------------ #
def generate_truth_table_and_forms(expr: str):
    """
    Парсит выражение, строит таблицу истинности с подвыражениями, а затем:
      - формирует числовую форму СДНФ (сумма минтермов) и СКНФ (произведение макстермов),
      - строит совершенные нормальные формы (СДНФ и СКНФ) с символами ¬, ∧, ∨,
      - выводит индексную форму функции.

    При выводе таблицы подвыражений:
      – переменные выводятся в алфавитном порядке,
      – затем комплексные подвыражения (отсортированные по глубине),
      – и, наконец, полное выражение (корневой узел).
    """
    # 1. Построить дерево и задать строковое представление подвыражений
    ast = parse_expression(expr)
    label_sub_expressions(ast)

    # 2. Собрать подвыражения для столбцов таблицы:
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

    # 3. Вывести заголовок таблицы истинности
    header = " | ".join(node.expr_str for node in columns)
    print(header)
    print("-" * len(header))

    # 4. Для вычисления индексной формы берём переменные в алфавитном порядке.
    vars_sorted = [n.var for n in var_nodes_sorted]
    n_vars = len(vars_sorted)

    truth_rows = []  # Список: (комбинация значений, f)
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

    # 5. Вычисляем минтермы и макстермы (числовые формы)
    minterms = []  # для f=1
    maxterms = []  # для f=0
    for combo, f_val in truth_rows:
        index = int("".join(str(bit) for bit in combo), 2)
        if f_val == 1:
            minterms.append(index)
        else:
            maxterms.append(index)

    # 6. Построение совершенных нормальных форм (СДНФ и СКНФ)
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

    # 7. Вычисление индексной формы
    binary_str = "".join(index_bits)
    index_value = int(binary_str, 2)
    binary_str_padded = format(index_value, f"0{2 ** n_vars}b")

    # 8. Вывод числовых форм и индексной формы
    print("\nСовершенная дизъюнктивная нормальная форма (СДНФ)")
    print(dnf_formula)
    print("\nСовершенная конъюнктивная нормальная форма (СКНФ)")
    print(cnf_formula)

    print("\nЧисловые формы:")
    print("(" + ", ".join(str(i) for i in sorted(minterms)) + ") ∧")
    print("(" + ", ".join(str(i) for i in sorted(maxterms)) + ") ∨")

    print("\nИндексная форма")
    print(f"{index_value} - {binary_str_padded}")

    # Добавляем возврат результата для целей тестирования
    return {
        'minterms': sorted(minterms),
        'maxterms': sorted(maxterms),
        'dnf_formula': dnf_formula,
        'cnf_formula': cnf_formula,
        'index_value': index_value,
        'binary_str_padded': binary_str_padded,
    }


def main():
    expr = input("Введите логическое выражение: ")
    print("\nТаблица истинности с подвыражениями:\n")
    generate_truth_table_and_forms(expr)


if __name__ == "__main__":
    main()
