import requests
import datetime
import csv


class Parser_CoronaVirus:

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
        self.url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv'
        req = requests.get(self.url)
        counter = 0
        if req.ok:
            self.answer.append("Информация о вирусе на сегодня:")
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
            with open("current_info.csv", 'w', encoding='utf-8') as csv_file:
                csv_file.writelines(req.text)

    def find_top_five(self, location: str, aspect: str):
        with open("current_info.csv", 'r') as state_file:
            data = dict()
            reader = csv.DictReader(state_file)
            for row in reader:
                if row[location] not in data.keys():
                    data[row[location]] = int(row[aspect])
                else:
                    data[row[location]] += int(row[aspect])
            temp = list(data.items())
            temp.sort(key=lambda value: value[1])
            temp = temp[::-1]
            for i in range(5):
                pair = temp[i]
                self.answer.append(pair[0] + " : " + str(pair[1]))

    def get_dynamics_info(self, target_country: str):
        self.write_data_corona()
        data = dict()
        with open("current_info.csv", "r") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row["Country_Region"] == target_country and not data:
                    data = {
                    "Confirmed": int(row["Confirmed"]),
                    "Deaths": int(row["Deaths"]),
                    "Recovered": int(row["Recovered"]),
                    "Active": int(row["Active"])}
                elif row["Country_Region"] == target_country:
                    data["Confirmed"] += int(row["Confirmed"])
                    data["Deaths"] += int(row["Deaths"])
                    data["Recovered"] += int(row["Recovered"])
                    data["Active"] += int(row["Active"])
        return data
