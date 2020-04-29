import requests
import datetime
import csv
import pymongo


class Parser_CoronaVirus:

    client = pymongo.MongoClient("localhost", 27017)
    db = client.mongo_bd
    corona_collection = db.corona_data

    def __init__(self, shift_date=0):
        self.shift_date = shift_date
        self.found_data = False
        self.answer = list()
        self.date = ""
        self.time = ""
        self.url = ""

    def write_data_corona(self):
        self.date = datetime.datetime.today() - datetime.timedelta(days=self.shift_date)
        self.time = self.date.strftime('%m-%d-%Y').split('-')

        # Идем по бд, если запись по текущей дате присутствует, мы не будем ничего парсить
        for entry in self.corona_collection.find():
            if "-".join(self.time) in entry.keys():
                self.answer.append("Информация о вирусе на сегодня:")
                return
        # *** Если записи нет. Парсим ***
        self.url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv'
        req = requests.get(self.url)
        limit = 0
        # Если была введена большая дата
        while not req.ok:
            self.date -= datetime.timedelta(days=1)
            self.time = self.date.strftime('%m-%d-%Y').split('-')
            link = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv"
            req = requests.get(link)
            if limit == 30:
                self.answer.append("Нет данных на заданное число")
                break
            limit += 1
        self.answer.append(f"Информация на сегодня пока нет. Последние данные на {'/'.join(self.time)} о вирусе:")

        # Парсим текущее число, либо самую близкую к текущему числу запись
        if req.ok:
            # Записали все данные, которые есть на сайте на данную дату
            with open("info.csv", "w", encoding='utf-8') as temp_data:
                temp_data.writelines(req.text)

            # Создаем словарь для данных одной даты, чтобы передать его в db
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
            # Добавляем запись в бд
            self.corona_collection.insert_one(current_data)
            current_data.clear()


    def find_top_five(self, location: str, aspect: str):
        data = dict()
        all_countries = dict()

        # Идем по бд и ищем запись на заданное число
        for entry in self.corona_collection.find():
            date = "-".join(self.time)
            if date in entry.keys():
                all_countries = entry[date]
                break

        # Идем по странам в записи и выбираем из них необходимые по location и aspect
        for country in all_countries:
            if country[location] not in data.keys():
                data[country[location]] = int(country[aspect])
            else:
                data[country[location]] += int(country[aspect])
        # Сортируем
        temp = list(data.items())
        temp.sort(key=lambda value: value[1])
        temp = temp[::-1]
        for i in range(5):
            pair = temp[i]
            self.answer.append(pair[0] + " : " + str(pair[1]))


    def get_dynamics_info(self, target_country: str):
        entry_value = dict()
        date = "-".join(self.time)
        data = {
            "Confirmed": 0,
            "Deaths": 0,
            "Recovered": 0,
            "Active": 0}

        # Идем по бд, если наткнулись на текущую дату, берем список со странами (entry_value)
        for entry in self.corona_collection.find():
            if date in entry.keys():
                entry_value = entry[date]
                break
        for country in entry_value:
            if country["Country_Region"] == target_country:
                data["Confirmed"] += int(country["Confirmed"])
                data["Deaths"] += int(country["Deaths"])
                data["Recovered"] += int(country["Recovered"])
                data["Active"] += int(country["Active"])
                self.found_data = True
        return data
