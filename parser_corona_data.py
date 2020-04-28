import requests
import datetime
import csv
import pymongo


class Parser_CoronaVirus:

    client = pymongo.MongoClient("localhost", 27017)
    db = client.mongo_bd
    corona_virus = db.corona_data

    def __init__(self, shift_date=0):
        self.shift_date = shift_date
        self.date = 0
        self.time = 0
        self.answer = list()
        self.status_write = False
        self.url = ""

    def write_data_corona(self):
        self.date = datetime.datetime.today() - datetime.timedelta(days=self.shift_date)
        self.time = self.date.strftime('%m-%d-%Y').split('-')
        for row in self.corona_virus.find():
            if "-".join(self.time) not in row.keys():
                self.url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv'
                req = requests.get(self.url)
                counter = 0
                if req.ok:
                    self.answer.append("Информация о вирусе на сегодня:")
                    break
                else:
                    # если была введена больше ранняя дата
                    while not req.ok:
                        self.date -= datetime.timedelta(days=1)
                        self.time = self.date.strftime('%m-%d-%Y').split('-')
                        link = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv"
                        req = requests.get(link)
                        if counter == 30:
                            self.answer.append("Нет данных на заданное число")
                            break
                        counter += 1
                    self.answer.append(f"Информация на сегодня пока нет. Последние данные на {'/'.join(self.time)} о вирусе:")
                    if req.ok:
                        self.status_write = True
                        # записали все данные, которые есть на сайте на данную дату
                        with open("info.csv", "w", encoding='utf-8') as parm_data:
                            parm_data.writelines(req.text)
                        #создаем словарь для данных одной даты, чтобы передать его в db
                        json_slovar = {}
                        json_slovar["-".join(self.time)] = []
                        with open("info.csv") as parm_data:
                            all_countries = csv.DictReader(parm_data)
                            for row in all_countries:
                                country = {'Province_State': row["Province_State"],
                                           'Country_Region': row["Country_Region"],
                                           'Confirmed': row['Confirmed'],
                                           'Deaths': row['Deaths'],
                                           'Recovered': row['Recovered'],
                                           'Active': row['Active']}
                                json_slovar["-".join(self.time)].append(country)
                        self.corona_virus.insert_one(json_slovar)
                        json_slovar.clear()


    def find_top_five(self, location: str, aspect: str):
        data = dict()
        all_dict_countries = {}
        for entry in self.corona_virus.find():
            date = "-".join(self.time)
            if date in entry.keys():
                all_dict_countries = entry[date]
                break

        for country in all_dict_countries:
            if country[location] not in data.keys():
                data[country[location]] = int(country[aspect])
            else:
                data[country[location]] += int(country[aspect])

        temp = list(data.items())
        temp.sort(key=lambda value: value[1])
        temp = temp[::-1]
        for i in range(5):
            pair = temp[i]
            self.answer.append(pair[0] + " : " + str(pair[1]))

    def get_dynamics_info(self, target_country: str):
        data = dict()
        for country in corona_virus.find():
            if country["Country_Region"] == target_country and not data:
                data = {
                "Confirmed": int(country["Confirmed"]),
                "Deaths": int(country["Deaths"]),
                "Recovered": int(country["Recovered"]),
                "Active": int(country["Active"])}
            elif country["Country_Region"] == target_country:
                data["Confirmed"] += int(country["Confirmed"])
                data["Deaths"] += int(country["Deaths"])
                data["Recovered"] += int(country["Recovered"])
                data["Active"] += int(country["Active"])
        return data
