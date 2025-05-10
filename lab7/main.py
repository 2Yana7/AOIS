from matrix import (
    create_binary_diagonal_matrix,
    print_matrix,
    get_word,
    get_addressed_column,
    set_value,
)
from logic_fun import f0, f5, f10, f15
from sum import binary_add_4bit


def main():
    N = 16
    matrix = None

    while True:
        print("\nВыберите пункт меню:")
        print("1. Создать и вывести матрицу 16×16")
        print("2. Считать слово или адресный столбец")
        print("3. Логические операции")
        print("4. Поиск по соответствию")
        print("5. Сложение полей A и B по ключу V")
        print("0. Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == '0':
            print("Выход.")
            break

        if choice == '1':
            matrix = create_binary_diagonal_matrix(N)
            print("\nСгенерированная матрица:")
            print_matrix(matrix, N)

        elif choice == '2':
            if matrix is None:
                print("Сначала сгенерируйте матрицу (пункт 1).")
                continue
            sub = input("1.Чтение слова\n2.Чтение адресного столбца\n ").strip()
            idx = int(input("Введите индекс (0–15): ").strip())
            if sub == '1':
                w = get_word(matrix, idx, N)
                print(f"Слово #{idx}: {''.join(map(str, w))}")
            else:
                d = get_addressed_column(matrix, idx, N)
                print(f"Адресный столбец: {''.join(map(str, d))}")

        elif choice == '3':
            if matrix is None:
                print("Сначала сгенерируйте матрицу (пункт 1).")
                continue
            a1 = int(input("Номер первого аргумента (0–15): ").strip())
            col1 = get_word(matrix, a1, N)
            a2 = int(input("Номер второго аргумента (0–15): ").strip())
            col2 = get_word(matrix, a2, N)
            r = int(input("Номер столбца для записи результата (0–15): ").strip())

            print("Выберите функцию:\n 1.f0\n 2.f5\n 3.f10\n 4.f15 ")
            fn = int(input("Номер функции (1-4): ").strip())
            if fn == 1:
                result = f0(col2)
            elif fn == 2:
                result = f5(col2)
            elif fn == 3:
                result = f10(col2)
            else:
                result = f15(col2)

            for i in range(N):
                set_value(matrix, (i + r) % N, r, result[i], N)

            print(f"Результат записи в столбец #{r}: {result}")
            print("Обновлённая матрица:")
            print_matrix(matrix, N)


        elif choice == '4':

            if matrix is None:
                print("Сначала сгенерируйте матрицу (пункт 1).")

                continue

            pat = input("Введите 16-битный шаблон (0/1, 16 символов): ").strip()

            if len(pat) != N or any(c not in '01' for c in pat):
                print("Неверный формат. Нужно ровно 16 символов 0/1.")

                continue

            pattern = [int(c) for c in pat]

            scores = []

            for j in range(N):
                word = get_word(matrix, j, N)

                match_count = sum(1 for i in range(N) if word[i] == pattern[i])

                scores.append((j, match_count))

            max_score = max(sc for _, sc in scores)

            best = [j for j, sc in scores if sc == max_score]

            print("\nСовпадения:")

            for j, sc in scores:
                print(f" {j:2}: {sc}")

            print(f"Максимум = {max_score}, слова = {best}")


        elif choice == '5':

            if matrix is None:
                print("Сначала сгенерируйте матрицу (пункт 1).")

                continue

            key = input("\nВведите ключ V (3 бита 000 - 111): ").strip()

            if len(key) != 3 or any(c not in '01' for c in key):
                print("Неверный формат ключа. Нужно ровно 3 символа 0/1.")

                continue

            print(f"Сложение полей A и B для V = {key}:\n")
            updated_cols = []
            for col in range(N):
                word = get_word(matrix, col, N)
                v = ''.join(map(str, word[0:3]))
                if v == key:
                    a = word[3:7]
                    b = word[7:11]
                    old_s = word[11:16]
                    new_s = binary_add_4bit(a, b)
                    updated_cols.append(col)
                    print(f"Найдено слово #{col}")
                    print(f"V = {v}")
                    print(f"A = {''.join(map(str, a))}")
                    print(f"B = {''.join(map(str, b))}")
                    print(f"S (старое) = {''.join(map(str, old_s))}")
                    print(f"S (новое ) = {''.join(map(str, new_s))}\n")
                    for i, bit in enumerate(new_s):
                        set_value(matrix, (11 + i + col) % N, col, bit, N)

            if not updated_cols:

                print(f"Слов с ключом V={key} не найдено.")

            else:

                print("Обновлённая матрица:")

                print_matrix(matrix, N)
        else:
            print("Неверный пункт, попробуйте ещё раз.")

if __name__ == "__main__":
    main()
