class Stroka:

    def __init__(self):
        self.strk = "Hello"

    def add(self, a): #добавление в строку элементов любого типа
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

    def change_length(self, i: int): #изменение длины строки
        if type(i) == float or i == len(self.strk):
            self.strk = self.strk
        else:
            if i > len(self.strk):
                self.strk = self.strk + (" " * (i - len(self.strk)))
            elif i < len(self.strk):
                self.strk = self.strk[:i]

    def change_stroka(self, index, podstroka):
        if type(index) == int:
            if index > len(self.strk) or len(podstroka) > len(self.strk) - index:
                self.strk = self.strk
            else:
                self.strk = self.strk[:index] + podstroka + self.strk[len(podstroka) + 1:]
        elif type(index) == list:
            for i in range(len(index) - 1):
                if i < len(self.strk):
                    self.strk = self.strk[:index[i]] + podstroka[i] + self.strk[index[i] + 1:]









