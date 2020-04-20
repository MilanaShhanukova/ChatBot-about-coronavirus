import re


class Stroka:

    def __init__(self, stroka):
        self.strk = stroka

    def add(self, a):  # добавление в строку элементов любого типа
        type_a = type(a)
        if type_a == str:
            self.strk = self.strk + a
        elif type_a == int:
            self.strk = self.strk + str(a)
        elif type_a == list or type_a == tuple:
            for i in a:
                self.strk = self.strk + str(i)
        elif type_a == dict:
            for key, value in a.items():
                self.strk = self.strk + str(key)
                if type(value) == list:
                    for i in value:
                        self.strk = self.strk + str(i)
                else:
                    self.strk = self.strk + str(value)

    def change_length(self, i: int):  # изменение длины строки
        if type(i) == float:
            raise TypeError
        else:
            if i < 0:
                raise IndexError
            elif i > len(self.strk):
                self.strk = self.strk + (" " * (i - len(self.strk)))
            elif i < len(self.strk):
                self.strk = self.strk[:i]
            elif i == 0:
                self.strk = ""

    def change_stroka(self, index, podstroka):  # изменение "внутренности" строки
        if type(index) == int:
            if index > len(self.strk) or len(podstroka) > len(self.strk) - index:
                self.strk = self.strk
            else:
                self.strk = self.strk[:index] + podstroka + self.strk[len(podstroka) + 1:]
        elif type(index) == list:
            for i in range(len(index) - 1):
                if i < len(self.strk):
                    self.strk = self.strk[:index[i]] + podstroka[i] + self.strk[index[i] + 1:]

    def format_stroka(self, type, delitel=" "):  # изменение типа строки, в лист, в словарь и число
        if type == "list":
            self.strk = self.strk.split(delitel)
        elif type == "dict":
            self.strk = self.strk.split(delitel)
            slovar_of_str = {}
            for i in range(len(self.strk) - 1):
                slovar_of_str[self.strk[i]] = i
        elif type == "int":
            if not self.strk.isdigit():
                raise ValueError("Несоответствующее значение")
            else:
                self.strk = int(self.strk)

    def match_stroka(self, str_for_match):  # метчинг строки
        return re.match(self.strk, str_for_match)
