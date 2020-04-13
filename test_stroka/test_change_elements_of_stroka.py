from stroka_change import Stroka

import unittest

class TestStroka(unittest.TestCase):
    def setUp(self):
        self.stroka = Stroka("Hello")

    def tearDown(self):
        self.stroka.strk = ""

    def test_change_one_element(self):
        self.stroka.change_stroka(1, "P")
        self.assertEqual(self.stroka.strk, "HPllo")

    def test_change_many_elements_different_indexes(self):
        self.stroka.change_stroka([1, 4, 0, 2, 5], ["a", "b", "c", "d", "e"])
        self.assertEqual(self.stroka.strk, "cadlb")

    def test_change_many_elements_(self):
        self.stroka.change_stroka(1, "yes")
        self.assertEqual(self.stroka.strk, "Hyeso")


if __name__ == "__main__":
    unittest.main()