import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime
import requests
import csv


class Statistics:

    URLS = {"confirmed": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
            "deaths": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
            "recovered": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"}

    def __init__(self):
        self.now = ""
        self.date = ""

    @staticmethod
    def download_data(r):
        with open("current_info.csv", 'w', encoding='utf-8') as now_data:
            now_data.writelines(r.text)

    def get_all_dates(self) -> list:
        dat = " "
        dates = list()
        while self.date < self.now:
            date_1 = self.date.strftime("%m/%d/%Y")
            date_1 = date_1.split('/')
            for i in range(len(date_1) - 1):
                date_1[i] = date_1[i].lstrip('0')
                dat = "/".join(date_1)
            dates.append(dat)
            self.date = self.date + datetime.timedelta(days=1)
        return dates

    @staticmethod
    def get_current_info(target_countries: list, dates: list) -> dict:
        info = dict()
        for country in target_countries:
            for date in dates:
                if date not in info.keys():
                    info[date] = []
                    info[date].append(int(country[date[:-2]]))
                else:
                    info[date].append(int(country[date[:-2]]))
        return info

    def write_data_in_data_set(self, location, dates: list) -> list:
        with open("current_info.csv", encoding='utf-8') as now_data:
            reader = csv.DictReader(now_data)
            data_set = list()
            target_countries = [row for row in reader if row["Country/Region"] == location]

            info = self.get_current_info(target_countries, dates)

            for data, value in info.items():
                data_set.append(sum(value))
            return data_set

    @staticmethod
    def correct_dates(dates: list) -> list:
        new_dates = list()
        for date in dates:
            # Если день от 1 до 9
            if len(date[:date.find('/')]) == 1:
                new_dates.append('0' + date[:-5])
            else:
                new_dates.append(date[:-5])
        return new_dates

    @staticmethod
    def graphic_draw(aspect: str, dates: list, data_set: list) -> None:
        y = data_set
        # соответствующие значения оси Y
        x = dates
        fig, ax = plt.subplots()
        ax.plot(x, y, color='r', linewidth=3)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(abs(data_set[-1] - data_set[0]) // 10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))
        #  Добавляем линии основной сетки:
        ax.grid(which='major', color='k')
        #  Включаем видимость вспомогательных делений:
        ax.minorticks_on()
        #  Теперь можем отдельно задавать внешний вид
        #  Вспомогательной сетки:
        ax.grid(which='minor',
                color='gray',
                linestyle=':')
        # Название оси х
        plt.xlabel('days', fontsize=15)
        # имя оси Y
        plt.ylabel(aspect, fontsize=15)

        fig.set_figwidth(12)
        fig.set_figheight(8)

        plt.savefig('graphic')
        plt.clf()

    def create_graphic_information(self, shift: int, location: str, aspect: str):
        self.now = datetime.datetime.today() - datetime.timedelta(days=1)
        self.date = datetime.datetime.today() - datetime.timedelta(days=int(shift))

        req = requests.get(self.URLS[aspect])

        self.download_data(req)

        dates = self.get_all_dates()

        data_set = self.write_data_in_data_set(location, dates)

        dates = self.correct_dates(dates)
        self.graphic_draw(aspect, dates, data_set)
