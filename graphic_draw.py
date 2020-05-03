import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime
import requests
import csv


class Statistics:

    URLS = {"confirmed": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
            "deaths": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
            "recovered": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv",
            "Active": ""}

    def __init__(self):
        self.dates = list()  # массив с датами до сегодня
        self.data_set = list()  # массив с координатами
        self.now = 0
        self.date = 0

    @staticmethod
    def download_data(r):
        with open("current_info.csv", 'w', encoding='utf-8') as now_data:
            now_data.writelines(r.text)

    # def data(self, shift: int, location: str, aspect: str):
    #     self.now = datetime.datetime.today() - datetime.timedelta(days=1)
    #     self.date = datetime.datetime.today() - datetime.timedelta(days=shift)
    #
    #     r = requests.get(self.URLS[aspect])

    def get_all_dates(self):
        dat = " "
        while self.date < self.now:
            date_1 = self.date.strftime("%m/%d/%Y")
            date_1 = date_1.split('/')
            for i in range(len(date_1) - 1):
                date_1[i] = date_1[i].lstrip('0')
                dat = "/".join(date_1)
            self.dates.append(dat)
            self.date = self.date + datetime.timedelta(days=1)

    def write_data(self, location):
        with open("current_info.csv", encoding='utf-8') as now_data:
            reader = csv.DictReader(now_data)
            info = {}
            for row in reader:
                if row["Country/Region"] == location:
                    for d in self.dates:
                        if d not in info.keys():
                            info[d] = []
                            info[d].append(int(row[d[0:-2]]))
                        else:
                            info[d].append(int(row[d[0:-2]]))
            for data, value in info.items():
                self.data_set.append(sum(value))

    def graphic_draw(self, aspect: str):
        y = self.data_set
        # соответствующие значения оси Y
        x = self.dates
        fig, ax = plt.subplots()
        ax.plot(x, y, color='r', linewidth=3)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(abs(self.data_set[-1] - self.data_set[0]) // 10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))
        #  Добавляем линии основной сетки:
        ax.grid(which='major', color='k')
        #  Включаем видимость вспомогательных делений:
        ax.minorticks_on()
        #  Теперь можем отдельно задавать внешний вид
        #  вспомогательной сетки:
        ax.grid(which='minor',
                color='gray',
                linestyle=':')

        # название оси х
        plt.xlabel('days', fontsize=15)
        # имя оси Y
        plt.ylabel(aspect, fontsize=15)

        fig.set_figwidth(12)
        fig.set_figheight(8)

        plt.savefig('graphic')
        plt.clf()

    def create_graphic_information(self, shift: int, location: str, aspect: str):
        self.now = datetime.datetime.today() - datetime.timedelta(days=1)
        self.date = datetime.datetime.today() - datetime.timedelta(days=shift)
        r = requests.get(self.URLS[aspect])
        self.download_data(r)
        self.get_all_dates()
        self.write_data(location)
        self.graphic_draw(aspect)
