import unittest
from ChangeString import Stroka


class TestStroka(unittest.TestCase):

    def setUp(self):
        self.stroka = Stroka("Hello")

    def tearDown(self):
        self.stroka.strk = ""

    def test_shorten_str(self):  # тест на срезы
        self.stroka.change_length(3)
        self.assertEqual(self.stroka.strk, "Hel")

    def test_shorten_str_empty(self):  # тест на изменение на отрицательную длину
        with self.assertRaises(IndexError):
            self.stroka.change_length(-3)

    def test_shorten_str_type(self):  # тест на изменение строки на размер типа float
        with self.assertRaises(TypeError):
            self.stroka.change_length(3.5)

    def test_longer_str(self):  # тест на добавление пробелов
        self.stroka.change_length(10)
        self.assertEqual(self.stroka.strk, "Hello     ")

    def test_change_to_minus(self):  # проверка на создание пустой строки
        self.stroka.change_length(0)
        self.assertFalse(self.stroka.strk)

    def test_change_if_not_empty(self):
        self.stroka.change_length(2)
        self.assertTrue(self.stroka.strk)


if __name__ == "__main__":
    unittest.main()
