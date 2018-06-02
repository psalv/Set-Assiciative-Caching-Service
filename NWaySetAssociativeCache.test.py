
import unittest
from time import sleep
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

- Both replacement algorithms
    - get afterwards
    - multiple times
"""

class PutTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = NWaySetAssociativeCache()

    def tearDown(self): del self.cache

    def add_single_item(self):
        # self.cache.put(1, 10)
        self.assertEqual(1, 1)


def suite(test_case, test_list):
    return unittest.TestSuite(map(test_case, test_list))


if __name__ == '__main__':

    put_suite = suite(PutTestCase, ['add_single_item'])
    unittest.main()
