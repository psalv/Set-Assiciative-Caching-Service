
import time
import unittest

from NWaySetAssociativeCache import NWaySetAssociativeCache


class NewObject(object):
    def __init__(self):
        pass


class PutTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = NWaySetAssociativeCache()

    def tearDown(self):
        del self.cache

    def test_put_single_item(self):
        self.cache.put(1, 10)
        time.sleep(0.1)
        instances = 0
        for current_set in self.cache._sets:
            if 1 in current_set:
                self.assertEqual(current_set[1].data, 10)
                instances += 1

        self.assertEqual(instances, 1)

    def test_put_multiple_items(self):
        for i in range(1, 9):
            self.cache.put(i, 10 * i)
        time.sleep(0.001)

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

        time.sleep(0.001)

        for i in range(len(keys)):
            instances = 0
            for current_set in self.cache._sets:
                if keys[i] in current_set:
                    self.assertEqual(current_set[keys[i]].data, data[i])
                    instances += 1

            self.assertEqual(instances, 1)


class GetTestCase(unittest.TestCase):
    def setUp(self):
        self.cache = NWaySetAssociativeCache()

    def tearDown(self):
        del self.cache

    def test_get_single_item(self):
        self.cache.put(1, 10)
        time.sleep(0.001)
        self.assertEqual(self.cache.get(1), 10)

    def test_get_multiple_items(self):
        for i in range(1, 9):
            self.cache.put(i, 10 * i)
        time.sleep(0.001)
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

        time.sleep(0.001)

        self.assertEqual(self.cache.get(1), 10)
        self.assertEqual(self.cache.get(2), 'foo')
        self.assertEqual(self.cache.get(2.03), 'bar')
        self.assertEqual(self.cache.get('fizz'), 20)
        self.assertEqual(self.cache.get(new_object1), new_object2)
        self.assertEqual(self.cache.get(new_object2), 'buzz')


class UpdateTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = NWaySetAssociativeCache()

    def tearDown(self):
        del self.cache

    def test_update_item(self):
        self.cache.put(1, 10)
        self.cache.put(1, 20)
        time.sleep(0.001)
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

        time.sleep(0.01)

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

        time.sleep(0.001)

        instances = 0
        for current_set in self.cache._sets:
            if newobject in current_set:
                self.assertEqual(current_set[newobject].data, 2)
                instances += 1
        self.assertEqual(instances, 1)

    def test_update_item_mixed_type_update(self):

        self.cache.put(1, 10)
        self.cache.put(1, 'foo')

        time.sleep(0.001)

        instances = 0
        for current_set in self.cache._sets:
            if 1 in current_set:
                self.assertEqual(current_set[1].data, 'foo')
                instances += 1
        self.assertEqual(instances, 1)

        newobject = NewObject()
        self.cache.put(1, newobject)

        time.sleep(0.001)

        instances = 0
        for current_set in self.cache._sets:
            if 1 in current_set:
                self.assertEqual(current_set[1].data, newobject)
                instances += 1
        self.assertEqual(instances, 1)

    def test_get_updated_item(self):
        self.cache.put(1, 10)
        self.cache.put(1, 20)
        time.sleep(0.01)
        self.assertEqual(self.cache.get(1), 20)


class InvalidInputTestCase(unittest.TestCase):

    def test_get_with_nonexistant_key(self):
        cache = NWaySetAssociativeCache()

        with self.assertRaises(ValueError):
            cache.get(1)

        del cache

    def test_initialization_with_invalid_replacement_algorithm(self):
        with self.assertRaises(ValueError):
            cache = NWaySetAssociativeCache(4, "LRV", 32)

        with self.assertRaises(ValueError):
            cache = NWaySetAssociativeCache(4, NewObject(), 32)


class ReplacementAlgorithmTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = NWaySetAssociativeCache()

    def tearDown(self):
        del self.cache

    def test_lru_algorithm_once(self):
        pass

    def test_lru_algorithm_multiple(self):
        pass

    def test_mru_algorithm_once(self):
        pass

    def test_mru_algorithm_multiple(self):
        pass

    def test_custom_algorithm(self):
        pass


class CacheSizeTestCase(unittest.TestCase):

    def test_single_set(self):
        pass

    def test_multiple_sets(self):
        pass

    def test_single_line(self):
        pass

    def test_multiple_lines(self):
        pass

    def test_very_large_cache(self):
        pass


if __name__ == '__main__':
    unittest.main()
