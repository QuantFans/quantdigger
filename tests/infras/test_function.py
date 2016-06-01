import unittest

from quantdigger.infras.function import *


class TestFunction(unittest.TestCase):

    def test_overload_setter(self):
        d = {}

        @overload_setter
        def setter(k, v):
            d[k] = v

        setter('k1', 'v1')
        self.assertEqual(d['k1'], 'v1')
        setter({'k2': 'v2', 'k1': 'v1_1'})
        self.assertEqual(d['k1'], 'v1_1')
        self.assertEqual(d['k2'], 'v2')
        setter(k1='v1_2', k2='v2_2')
        self.assertEqual(d['k1'], 'v1_2')
        self.assertEqual(d['k2'], 'v2_2')
        setter('k1', 'v1_3', k2='v2_3')
        self.assertEqual(d['k1'], 'v1_3')
        self.assertEqual(d['k2'], 'v2_3')


if __name__ == '__main__':
    unittest.main()
