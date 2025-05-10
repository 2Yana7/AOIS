import unittest
import io
import contextlib

from lab6 import HashTable, parse_value  

class TestHashTable(unittest.TestCase):
    def test_min_capacity(self):
        ht = HashTable(capacity=5, debug=False)
        self.assertEqual(ht.capacity, 20)

    def test_initial_size(self):
        ht = HashTable(capacity=30, debug=False)
        self.assertEqual(len(ht), 10)

    def test_repr(self):
        ht = HashTable(capacity=25, debug=False)
        self.assertEqual(repr(ht), "HashTable(size=10, capacity=25)")

    def test_hash_zero_offset(self):
        ht = HashTable(capacity=11, offset=0, debug=False)
        self.assertEqual(ht._hash(1), hash(1) % 11)

    def test_hash_nonzero_offset(self):
        ht = HashTable(capacity=11, offset=3, debug=False)
        self.assertEqual(ht._hash(1), ((hash(1) % 11) + 3) % 11)

    def test_probe_sequence_wrap(self):
        ht = HashTable(capacity=5, debug=False)
        # Принудительно устанавливаем меньшую ёмкость для теста
        ht.capacity = 5
        seq = ht._probe_sequence(3)
        expected = [3, 4, 0, 1, 2]
        for e in expected:
            self.assertEqual(next(seq), e)

    def test_insert_new_key(self):
        ht = HashTable(capacity=20, debug=False)
        prev = len(ht)
        with contextlib.redirect_stdout(io.StringIO()):
            ht.insert("foo", 123)
        self.assertEqual(len(ht), prev + 1)
        slot = ht._find_slot("foo", for_insert=False)
        self.assertEqual(ht.table[slot], ("foo", 123))

    def test_insert_existing_key_updates_value(self):
        ht = HashTable(capacity=20, debug=False)
        with contextlib.redirect_stdout(io.StringIO()):
            ht.insert("bar", 1)
        prev = len(ht)
        with contextlib.redirect_stdout(io.StringIO()):
            ht.insert("bar", 2)
        self.assertEqual(len(ht), prev)
        slot = ht._find_slot("bar", for_insert=False)
        self.assertEqual(ht.table[slot], ("bar", 2))

    def test_insert_table_full(self):
        ht = HashTable(capacity=20, debug=False)
        ht.table = [(i, i) for i in range(ht.capacity)]
        ht.size = ht.capacity
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ht.insert(999, 999)
        self.assertIn("Ошибка: таблица заполнена", buf.getvalue())

    def test_get_existing(self):
        ht = HashTable(capacity=20, debug=False)
        with contextlib.redirect_stdout(io.StringIO()):
            ht.insert("key", 42)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ht.get("key")
        self.assertIn("Значение для ключа 'key': 42", buf.getvalue())

    def test_get_nonexistent(self):
        ht = HashTable(capacity=20, debug=False)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ht.get("nope")
        self.assertIn("Ключ 'nope' не найден", buf.getvalue())

    def test_delete_existing(self):
        ht = HashTable(capacity=20, debug=False)
        with contextlib.redirect_stdout(io.StringIO()):
            ht.insert("to_del", 5)
        prev = len(ht)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ht.delete("to_del")
        self.assertEqual(len(ht), prev - 1)
        slot = ht._find_slot("to_del", for_insert=True)
        self.assertIs(ht.table[slot], HashTable.DELETED)
        self.assertIn("Ключ 'to_del' удалён", buf.getvalue())

    def test_delete_nonexistent(self):
        ht = HashTable(capacity=20, debug=False)
        prev = len(ht)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ht.delete("xyz")
        self.assertEqual(len(ht), prev)
        self.assertIn("удаление не выполнено", buf.getvalue())

    def test_len_and_size_property(self):
        ht = HashTable(capacity=20, debug=False)
        self.assertEqual(len(ht), ht.size)

    def test_print_table_format(self):
        ht = HashTable(capacity=5, debug=False)
        ht.table = [None] * ht.capacity
        ht.size = 0
        with contextlib.redirect_stdout(io.StringIO()):
            ht.insert(1, 10)
            ht.insert(2, 20)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ht.print_table()
        out = buf.getvalue().splitlines()
        self.assertTrue(out[0].startswith('+'))
        self.assertIn('Idx', out[1])
        self.assertTrue(any('1' in line and '10' in line for line in out))

    def test_offset_affects_insertion(self):
        ht1 = HashTable(capacity=11, offset=0, debug=False)
        ht2 = HashTable(capacity=11, offset=5, debug=False)
        with contextlib.redirect_stdout(io.StringIO()):
            ht1.insert('a', 1)
            ht2.insert('a', 1)
        slot1 = ht1._find_slot('a', for_insert=False)
        slot2 = ht2._find_slot('a', for_insert=False)
        self.assertNotEqual(slot1, slot2)

    def test_parse_value_int(self):
        self.assertEqual(parse_value("123"), 123)

    def test_parse_value_float(self):
        self.assertAlmostEqual(parse_value("3.14"), 3.14, places=5)

    def test_parse_value_str(self):
        self.assertEqual(parse_value("abc"), "abc")

    def test_multiple_deletions(self):
        ht = HashTable(capacity=20, debug=False)
        with contextlib.redirect_stdout(io.StringIO()):
            ht.insert('x', 0)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ht.delete('x')
            ht.delete('x')
        out = buf.getvalue()
        self.assertEqual(out.count("Ключ 'x' удалён"), 1)
        self.assertIn("удаление не выполнено", out)

    def test_find_slot_full_cycle(self):
        ht = HashTable(capacity=7, offset=0, debug=False)
        ht.table = [("foo", 1)] * ht.capacity
        slot = ht._find_slot('any', for_insert=False)
        self.assertIsNone(slot)

    def test_insert_reuses_deleted_slot(self):
        ht = HashTable(capacity=20, debug=False)
        with contextlib.redirect_stdout(io.StringIO()):
            ht.insert('reuse', 1)
            ht.delete('reuse')
            prev = len(ht)
            ht.insert('new', 2)
        # Проверяем, что размер увеличился и ключ 'new' присутствует
        self.assertEqual(len(ht), prev + 1)
        slot_new = ht._find_slot('new', for_insert=False)
        self.assertIsNotNone(slot_new)
        self.assertEqual(ht.table[slot_new], ('new', 2))

    def test_capacity_property(self):
        ht = HashTable(capacity=50, debug=False)
        self.assertEqual(ht.capacity, 50)
        ht_small = HashTable(capacity=10, debug=False)
        self.assertEqual(ht_small.capacity, 20)

    def test_zero_offset_default(self):
        ht = HashTable(debug=False)
        self.assertEqual(ht.offset, 0)

if __name__ == '__main__':
    unittest.main()
