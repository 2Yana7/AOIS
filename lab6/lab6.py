class HashTable:

    DELETED = object()

    def __init__(self, capacity=20, offset=0, debug=True):
        # Гарантируем минимальную ёмкость в 20
        self.capacity = max(capacity, 20)
        self.offset = offset
        self.debug = debug
        self.size = 0
        self.table = [None] * self.capacity

        initial = [1, 1 + self.capacity, 1 + 2*self.capacity,
                   2, 2 + self.capacity,
                   3, 4, 5, 6, 7]
        for key in initial:
            self.insert(key, key * 10)

    def _hash(self, key):
        return (hash(key) % self.capacity + self.offset) % self.capacity

    def _probe_sequence(self, start):
        idx = start
        while True:
            yield idx
            idx = (idx + 1) % self.capacity

    def _find_slot(self, key, for_insert=False):
        start = self._hash(key)
        if self.debug:
            print(f"[ШАГ] Ключ: {key}, стартовый индекс: {start}")
        first_deleted = None
        for idx in self._probe_sequence(start):
            cell = self.table[idx]
            if self.debug:
                print(f"[ШАГ] Проверяем индекс {idx}: {cell}")
            if cell is None:
                if self.debug:
                    print(f"[ШАГ] Возвращаем индекс для {'вставки' if for_insert else 'поиска'}: {idx}")
                return first_deleted if (for_insert and first_deleted is not None) else (idx if for_insert else None)
            if cell is HashTable.DELETED:
                if for_insert and first_deleted is None:
                    first_deleted = idx
                    if self.debug:
                        print(f"[ШАГ] Запомнили первую удалённую ячейку: {idx}")
            else:
                k, _ = cell
                if k == key:
                    if self.debug:
                        print(f"[ШАГ] Найден ключ в индексе {idx}")
                    return idx
            if idx == (start - 1) % self.capacity:
                if self.debug:
                    print(f"[ШАГ] Прошли полный круг поиска")
                return first_deleted if for_insert else None

    def insert(self, key, value):
        slot = self._find_slot(key, for_insert=True)
        if slot is None:
            print("Ошибка: таблица заполнена")
            return
        if self.table[slot] is None or self.table[slot] is HashTable.DELETED:
            self.size += 1
        self.table[slot] = (key, value)
        if self.debug:
            print(f"[ИТОГ] ({key}, {value}) -> ячейка {slot}\n")

    def get(self, key):
        slot = self._find_slot(key, for_insert=False)
        if slot is not None and self.table[slot] is not HashTable.DELETED:
            value = self.table[slot][1]
            print(f"Значение для ключа '{key}': {value}")
            if self.debug:
                print(f"[ШАГ] найдено в {slot}\n")
        else:
            print(f"Ключ '{key}' не найден")
            if self.debug:
                print(f"[ШАГ] результат None\n")

    def delete(self, key):
        slot = self._find_slot(key, for_insert=False)
        if slot is None or self.table[slot] is HashTable.DELETED:
            print(f"Ключ '{key}' не найден, удаление не выполнено")
            if self.debug:
                print(f"[ШАГ] ничего не удалено\n")
            return
        self.table[slot] = HashTable.DELETED
        self.size -= 1
        print(f"Ключ '{key}' удалён")
        if self.debug:
            print(f"[ШАГ] удалено из {slot}\n")

    def print_table(self):
        idx_w = len(str(self.capacity - 1))
        key_col, val_col = [], []
        for cell in self.table:
            if cell is None:
                key_col.append("None"); val_col.append("")
            elif cell is HashTable.DELETED:
                key_col.append("<DEL>"); val_col.append("")
            else:
                k, v = cell
                key_col.append(str(k)); val_col.append(str(v))
        key_w = max(len(s) for s in key_col)
        val_w = max(len(s) for s in val_col)
        line = f"+{'-'*(idx_w+2)}+{'-'*(key_w+2)}+{'-'*(val_w+2)}+"
        print(line)
        print(f"| {'Idx'.center(idx_w)} | {'Key'.center(key_w)} | {'Value'.center(val_w)} |")
        print(line)
        for i, (k, v) in enumerate(zip(key_col, val_col)):
            print(f"| {str(i).rjust(idx_w)} | {k.ljust(key_w)} | {v.ljust(val_w)} |")
        print(line)

    def __len__(self):
        return self.size

    def __repr__(self):
        return f"HashTable(size={self.size}, capacity={self.capacity})"


def parse_value(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

if __name__ == "__main__":
    ht = HashTable(capacity=11, offset=0, debug=True)
    while True:
        print("\nВыберите действие:")
        print("1. Добавить элемент")
        print("2. Получить значение по ключу")
        print("3. Удалить элемент")
        print("4. Показать таблицу")
        print("5. Выход")
        choice = input("Введите номер (1-5): ").strip()
        if choice == '1':
            raw = input("Введите ключ: ").strip()
            key = parse_value(raw)
            val = parse_value(input("Введите значение: ").strip())
            ht.insert(key, val)
        elif choice == '2':
            raw = input("Введите ключ: ").strip()
            key = parse_value(raw)
            ht.get(key)
        elif choice == '3':
            raw = input("Введите ключ для удаления: ").strip()
            key = parse_value(raw)
            ht.delete(key)
        elif choice == '4':
            ht.print_table()
        elif choice == '5':
            print("Завершение работы")
            break
        else:
            print("Неверный выбор, попробуйте снова")
