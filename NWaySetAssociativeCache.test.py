
import unittest
import time
from NWaySetAssociativeCache import NWaySetAssociativeCache

"""
Tests to create:
- Insert / Get / update
    - multiple items
    - different/mixed types

- Invalid input
    - get
    - custom replacement

- Very large input

- Caches of different sizes

- Both replacement algorithms
    - get afterwards
    - multiple times
"""

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

    def test_put_update_item(self):
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

    def test_get_update_item(self):
        self.cache.put(1, 10)
        self.cache.put(1, 20)
        time.sleep(0.001)
        self.assertEqual(self.cache.get(1), 20)


if __name__ == '__main__':
    unittest.main()
