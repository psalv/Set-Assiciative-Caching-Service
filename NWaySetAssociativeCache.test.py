
import time
import unittest

from NWaySetAssociativeCache import NWaySetAssociativeCache


class NewObject(object):
    def __init__(self):
        pass


class PutTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = NWaySetAssociativeCache(n)

    def tearDown(self):
        del self.cache

    def test_put_single_item(self):
        self.cache.put(1, 10)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        instances = 0
        for current_set in self.cache._sets:
            if 1 in current_set:
                self.assertEqual(current_set[1].data, 10)
                instances += 1

        self.assertEqual(instances, 1)

    def test_put_multiple_items(self):
        for i in range(1, 9):
            self.cache.put(i, 10 * i)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        for i in range(1, 9):
            instances = 0
            for current_set in self.cache._sets:
                if i in current_set:
                    self.assertEqual(current_set[i].data, 10 * i)
                    instances += 1

            self.assertEqual(instances, 1)

    def test_put_items_of_mixed_types(self):
        new_object1 = NewObject()
        new_object2 = NewObject()

        keys = [1, 2, 2.03, 'fizz', new_object1, new_object2]
        data = [10, 'foo', 'bar', 20, new_object2, 'buzz']

        for i in range(len(keys)):
            self.cache.put(keys[i], data[i])

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        for i in range(len(keys)):
            instances = 0
            for current_set in self.cache._sets:
                if keys[i] in current_set:
                    self.assertEqual(current_set[keys[i]].data, data[i])
                    instances += 1

            self.assertEqual(instances, 1)


class GetTestCase(unittest.TestCase):
    def setUp(self):
        self.cache = NWaySetAssociativeCache(n)

    def tearDown(self):
        del self.cache

    def test_get_single_item(self):
        self.cache.put(1, 10)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(self.cache.get(1), 10)

    def test_get_multiple_items(self):
        for i in range(1, 9):
            self.cache.put(i, 10 * i)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        for i in range(1, 9):
            self.assertEqual(self.cache.get(i), 10 * i)

    def test_get_items_of_mixed_types(self):
        self.cache.put(1, 10)
        self.cache.put(2, 'foo')
        self.cache.put(2.03, 'bar')
        self.cache.put('fizz', 20)

        new_object1 = NewObject()
        new_object2 = NewObject()

        self.cache.put(new_object1, new_object2)
        self.cache.put(new_object2, 'buzz')

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(self.cache.get(1), 10)
        self.assertEqual(self.cache.get(2), 'foo')
        self.assertEqual(self.cache.get(2.03), 'bar')
        self.assertEqual(self.cache.get('fizz'), 20)
        self.assertEqual(self.cache.get(new_object1), new_object2)
        self.assertEqual(self.cache.get(new_object2), 'buzz')


class UpdateTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = NWaySetAssociativeCache(n)

    def tearDown(self):
        del self.cache

    def test_update_item(self):
        self.cache.put(1, 10)
        self.cache.put(1, 20)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        instances = 0
        for current_set in self.cache._sets:
            if 1 in current_set:
                self.assertEqual(current_set[1].data, 20)
                instances += 1

        self.assertEqual(instances, 1)

    def test_update_multiple_items(self):
        for i in range(1, 9):
            self.cache.put(i, 10 * i)

        for i in range(1, 9):
            self.cache.put(i, 10 * i + 5)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        for i in range(1, 9):
            instances = 0
            for current_set in self.cache._sets:
                if i in current_set:
                    self.assertEqual(current_set[i].data, 10 * i + 5)
                    instances += 1

            self.assertEqual(instances, 1)

    def test_update_mixed_types(self):
        newobject = NewObject()
        self.cache.put(newobject, 1)
        self.cache.put(newobject, 2)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        instances = 0
        for current_set in self.cache._sets:
            if newobject in current_set:
                self.assertEqual(current_set[newobject].data, 2)
                instances += 1
        self.assertEqual(instances, 1)

    def test_update_item_mixed_type_update(self):

        self.cache.put(1, 10)
        self.cache.put(1, 'foo')

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        instances = 0
        for current_set in self.cache._sets:
            if 1 in current_set:
                self.assertEqual(current_set[1].data, 'foo')
                instances += 1
        self.assertEqual(instances, 1)

        newobject = NewObject()
        self.cache.put(1, newobject)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        instances = 0
        for current_set in self.cache._sets:
            if 1 in current_set:
                self.assertEqual(current_set[1].data, newobject)
                instances += 1
        self.assertEqual(instances, 1)

    def test_get_updated_item(self):
        self.cache.put(1, 10)
        self.cache.put(1, 20)

        while not self.cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(self.cache.get(1), 20)


class InvalidInputTestCase(unittest.TestCase):

    def test_get_with_nonexistant_key(self):
        cache = NWaySetAssociativeCache()

        with self.assertRaises(ValueError):
            cache.get(1)

    def test_initialization_with_invalid_replacement_algorithm(self):
        with self.assertRaises(ValueError):
            cache = NWaySetAssociativeCache(4, "LRV", 32)

        with self.assertRaises(ValueError):
            cache = NWaySetAssociativeCache(4, NewObject(), 32)

        with self.assertRaises(ValueError):
            cache = NWaySetAssociativeCache(4, 3, 32)

        def mock():
            pass

        cache = NWaySetAssociativeCache(4, mock, 32)


class ReplacementAlgorithmTestCase(unittest.TestCase):

    def test_replacement_in_memory(self):
        cache = NWaySetAssociativeCache(1, 'LRU', 1)
        cache.put(1, 10)
        cache.put(2, 20)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(len(cache._sets[0]), 1)
        self.assertEqual(cache._sets[0][2].data, 20)

    def test_lru_algorithm_once(self):
        cache = NWaySetAssociativeCache(1, 'LRU', 4)
        for i in range(1, 6):
            cache.put(i, 10 * i)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(len(cache._sets[0]), 4)

        with self.assertRaises(ValueError):
            cache.get(1)

        for i in range(2, 6):
            self.assertEqual(cache.get(i), i * 10)

    def test_lru_algorithm_multiple(self):
        cache = NWaySetAssociativeCache(1, 'LRU', 4)
        for i in range(1, 9):
            cache.put(i, 10 * i)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(len(cache._sets[0]), 4)

        for i in range(1, 5):
            with self.assertRaises(ValueError):
                cache.get(i)

        for i in range(5, 9):
            self.assertEqual(cache.get(i), i * 10)

    def test_mru_algorithm_once(self):
        cache = NWaySetAssociativeCache(1, 'MRU', 2)
        cache.put(1, 10)
        cache.put(2, 20)
        cache.put(3, 30)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(len(cache._sets[0]), 2)
        self.assertEqual(cache._sets[0][1].data, 10)
        self.assertEqual(cache._sets[0][3].data, 30)

    def test_mru_algorithm_multiple(self):
        cache = NWaySetAssociativeCache(1, 'MRU', 4)
        for i in range(1, 9):
            cache.put(i, 10 * i)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(len(cache._sets[0]), 4)
        for i in range(4, 8):
            with self.assertRaises(ValueError):
                cache.get(i)

        for i in [1, 2, 3, 8]:
            self.assertEqual(cache.get(i), i * 10)

    def test_custom_algorithm(self):

        def mru_custom_algorithm(class_instance, current_set_id):
            return NWaySetAssociativeCache.mru(class_instance, current_set_id)

        cache = NWaySetAssociativeCache(1, mru_custom_algorithm, 2)
        cache.put(1, 10)
        cache.put(2, 20)
        cache.put(3, 20)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        with self.assertRaises(ValueError):
            cache.get(2)

        cache.put(4, 40)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        with self.assertRaises(ValueError):
            cache.get(3)


class CacheSizeTestCase(unittest.TestCase):

    def test_single_line(self):
        cache = NWaySetAssociativeCache(n, "LRU", 1)

        cache.put(1, 10)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(cache.get(1), 10)

        cache.put(2, 20)

        time.sleep(time_spacer)
        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(cache.get(2), 20)

        cache.put('foo', 'bar')

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(cache.get('foo'), 'bar')

    def test_multiple_lines(self):
        cache = NWaySetAssociativeCache(n, "LRU", 128)

        cache.put(1, 10)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(cache.get(1), 10)

        cache.put(2, 20)

        time.sleep(time_spacer)
        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(cache.get(2), 20)

        cache.put('foo', 'bar')

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        self.assertEqual(cache.get('foo'), 'bar')

    def test_large_input(self):
        cache = NWaySetAssociativeCache(1, "LRU", 128)

        for i in range(1, 10000):
            cache.put(i, i)

        while not cache._jobs_queue.is_empty():
            time.sleep(time_spacer)

        for i in range(1, 10000 - 128):
            with self.assertRaises(ValueError):
                cache.get(i)

        for i in range(10000 - 128 + 1, 10000):
            self.assertEqual(cache.get(i), i)


if __name__ == '__main__':
    time_spacer = 0.001

    n = 1
    unittest.main(exit=False)
    n = 4
    unittest.main(exit=False)
    n = 32
    unittest.main(exit=False)

