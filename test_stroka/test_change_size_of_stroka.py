from stroka_change import Stroka

import unittest

class TestStroka(unittest.TestCase):
    def setUp(self):
        self.stroka = Stroka()

    def tearDown(self):
        self.stroka.strk = "Hello"

    def test_shorten_str(self): #тест на срезы
        self.stroka.change_length(3)
        self.assertEqual(self.stroka.strk, "Hel")

    def test_shorten_str(self): #тест на изменение строки на размер типа float
        self.stroka.change_length(3.5)
        self.assertEqual(self.stroka.strk, "Hello")

    def test_longer_str(self): #тест на добавление пробелов
        self.stroka.change_length(10)
        self.assertEqual(self.stroka.strk, "Hello     ")

if __name__ == "__main__":
    unittest.main()