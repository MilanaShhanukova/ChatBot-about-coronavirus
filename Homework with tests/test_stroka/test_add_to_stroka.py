import unittest
from ChangeString import Stroka


class TestStroka(unittest.TestCase):

    def setUp(self):
        self.stroka = Stroka("Hello")

    def tearDown(self):
        self.stroka.strk = ""

    def test_add_str(self):
        self.stroka.add(" World")
        self.assertEqual(self.stroka.strk, "Hello World")

    def test_add_intfloat(self):
        self.stroka.add(8)
        self.assertEqual(self.stroka.strk, "Hello8")

    def test_add_list(self):
        self.stroka.add([8, " World"])
        self.assertEqual(self.stroka.strk, "Hello8 World")

    def test_add_tuple(self):
        self.stroka.add((8, " World"))
        self.assertEqual(self.stroka.strk, "Hello8 World")

    def test_add_dict(self):
        self.stroka.add({"World": 8})
        self.assertEqual(self.stroka.strk, "HelloWorld8")


if __name__ == "__main__":
    unittest.main()
