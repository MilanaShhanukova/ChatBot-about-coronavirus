import unittest
from ChangeString import Stroka

class TestStroka(unittest.TestCase):
    def setUp(self):
        self.stroka = Stroka("Hi I am testing you")

    def tearDown(self):
        self.stroka.strk = ""

    def test_str_to_list(self):
        self.stroka.format_stroka("list")
        self.assertIs(type(self.stroka.strk), list)

    def test_insides_of_str_to_list(self):
        self.stroka.format_stroka("list")
        self.assertIn('Hi', self.stroka.strk)

    def test_str_to_int_false(self):
        with self.assertRaises(ValueError):
            self.stroka.format_stroka("int")

    def test_matching(self):
        self.assertIsNone(self.stroka.match_stroka("Not our string"))

if __name__ == "__main__":
    unittest.main()