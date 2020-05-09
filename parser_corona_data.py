import requests
import datetime
import csv
import pymongo
from enum import Enum


class options(Enum):
    ENTRY_EXISTS_IN_DB = 1
    NOT_INFO = 2


class Parser_CoronaVirus:
    
    time = list()

    def __init__(self):
        self.found_data = False
        self.answer = list()
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = client.mongo_bd
        self.corona_collection = db.corona_data

    # **** WRITE_CORONA_DATA
    # Анализируя дата определяет, есть ли уже данные в дб, коректна ли дата. Если данных в дб еще нет, возвращает запрос
    # для парсинга данных
    def find_suitable_date(self, shift_date=0):
        date = datetime.datetime.today() - datetime.timedelta(days=shift_date)
        self.time = date.strftime('%m-%d-%Y').split('-')
        # Идем по бд, если запись по текущей дате присутствует, мы не будем ничего парсить
        for entry in self.corona_collection.find():
            if "-".join(self.time) in entry.keys():
                return options.ENTRY_EXISTS_IN_DB

        # *** Если записи нет. Находим ближайшую дату ***
        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv'
        req = requests.get(url)
        limit = 0
        while not req.ok:
            date -= datetime.timedelta(days=1)
            self.time = date.strftime('%m-%d-%Y').split('-')
            link = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv"
            req = requests.get(link)
            if limit == 30:
                return options.NOT_INFO
            limit += 1
        self.answer.append(f"Информация на сегодня пока нет. Последние данные на {'/'.join(self.time)} о вирусе:")
        return req

    # Достает данные по запросу
    def write_data_corona(self, req) -> dict:
        # Парсим текущее число, либо самую близкую к текущему числу запись
        if req.ok:
            with open("info.csv", "w", encoding='utf-8') as temp_data:
                temp_data.writelines(req.text)
            current_data = {"-".join(self.time): []}

            # Открывае csv файл и перекидываем информацию в бд
            with open("info.csv") as temp_data:
                all_countries = csv.DictReader(temp_data)
                for row in all_countries:
                    country = {'Province_State': row["Province_State"],
                               'Country_Region': row["Country_Region"],
                               'Confirmed': row['Confirmed'],
                               'Deaths': row['Deaths'],
                               'Recovered': row['Recovered'],
                               'Active': row['Active']}
                    current_data["-".join(self.time)].append(country)
            return current_data

    # Находит данные о страных по числу
    def find_actual_data(self, shift_date=0) -> None:
        result = self.find_suitable_date(shift_date)
        # Если слишком большая или неправильная дата
        if result == options.NOT_INFO:
            self.answer.append("Нет данных на заданное число")
            return
        # Если информация уже хранится в дб
        elif result == options.ENTRY_EXISTS_IN_DB:
            self.answer.append("Информация о вирусе на сегодня:")
            return
        # Парсим и добавляем в бд
        else:
            self.corona_collection.insert_one(self.write_data_corona(result))

    # **** FIND_TOP_FIVE ****
    # Находит список стран по дате
    def find_value_by_date(self, date) -> list:
        # Идем по бд и ищем запись на заданное число
        return [entry[date] for entry in self.corona_collection.find() if date in entry.keys()][0]

    # Выбирает страны по локации и аспекту из списква всех стран
    @staticmethod
    def find_target_countries_by_loc_and_asp(all_countries: list, location: str, aspect: str) -> dict:
        data = dict()
        for country in all_countries:
            data[country[location]] = data.get(country[location], 0) + int(country[aspect])
        return data

    # Сортирует выбранные страны в порядке возрастания
    @staticmethod
    def sort_countries_by_aspect(data: dict) -> list:
        # Сортируем страны
        temp = list(data.items())
        temp.sort(key=lambda value: value[1])
        return temp[::-1]

    # Находит пятерку стран по значению location и aspect
    def find_top_five(self, location: str, aspect: str) -> None:
        # Достаем список со странами по дате из бд
        all_countries = self.find_value_by_date('-'.join(self.time))
        # Идем по странам в записи и выбираем из них необходимые по location и aspect
        data = self.find_target_countries_by_loc_and_asp(all_countries, location, aspect)

        # Сортируем страны
        sorted_countries = self.sort_countries_by_aspect(data)
        self.answer += [sorted_countries[i][0] + " : " + str(sorted_countries[i][1]) for i in range(5)]

    # **** GET_DYNAMICS_INFO****
    # Находим информацию в бд по текущей стране
    def get_info(self, entry_value: list, target_country: str) -> dict:
        data = dict()
        for country in entry_value:
            if country["Country_Region"] == target_country:
                data["Confirmed"] = data.get("Confirmed", 0) + int(country["Confirmed"])
                data["Deaths"] = data.get("Deaths", 0) + int(country["Deaths"])
                data["Recovered"] = data.get("Recovered", 0) + int(country["Recovered"])
                data["Active"] = data.get("Active", 0) + int(country["Active"])
                self.found_data = True
        return data

    def get_dynamics_info(self, target_country: str) -> dict:
        # Идем по бд, если наткнулись на текущую дату, берем список со странами (self.find_value_by_date(date)))
        return self.get_info(self.find_value_by_date("-".join(self.time)), target_country)
