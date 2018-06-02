
import unittest
import time
from NWaySetAssociativeCache import NWaySetAssociativeCache


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
        time.sleep(0.1)

        for i in range(1, 9):
            instances = 0
            for current_set in self.cache._sets:
                if i in current_set:
                    self.assertEqual(current_set[i].data, 10 * i)
                    instances += 1

            self.assertEqual(instances, 1)

    def test_put_items_of_mixed_types(self):
        pass


class GetTestCase(unittest.TestCase):
    def setUp(self):
        self.cache = NWaySetAssociativeCache()

    def tearDown(self):
        del self.cache

    def test_get_single_item(self):
        self.cache.put(1, 10)
        time.sleep(0.1)
        self.assertEqual(self.cache.get(1), 10)

    def test_get_multiple_items(self):
        for i in range(1, 9):
            self.cache.put(i, 10 * i)
        time.sleep(0.1)
        for i in range(1, 9):
            self.assertEqual(self.cache.get(i), 10 * i)

    def test_get_items_of_mixed_types(self):

        class NewObject(object):
            def __init__(self):
                pass

        self.cache.put(1, 10)
        self.cache.put(2, 'foo')
        self.cache.put(2.03, 'bar')
        self.cache.put('fizz', 20)

        new_object1 = NewObject()
        new_object2 = NewObject()

        self.cache.put(new_object1, new_object2)
        self.cache.put(new_object2, 'buzz')

        time.sleep(0.1)

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
        pass

    def test_update_multiple_items(self):
        pass

    def test_update_item_mixed_type(self):
        pass

    def test_get_updated_item(self):
        self.cache.put(1, 10)
        self.cache.put(1, 20)
        time.sleep(0.001)
        self.assertEqual(self.cache.get(1), 20)


class InvalidInputTestCase(unittest.TestCase):

    def test_get_with_nonexistant_key(self):
        cache = NWaySetAssociativeCache()

        del cache

    def test_initialization_with_invalid_replacement_algorithm(self):
        pass


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
