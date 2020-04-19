import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime
import requests
import csv


class Statistics:
    def __init__(self):
        pass

    @staticmethod
    def data(shift: int, location: str):
        now = datetime.datetime.today()
        r = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/\
        	csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
        now = now - datetime.timedelta(days=1)
        date = now - datetime.timedelta(days=shift)
        dates = []  # массив с датами до сегодня
        data_set = []  # массив с координатами
        with open("current_info.csv", 'w', encoding='utf-8') as now_data:
            now_data.writelines(r.text)
        with open("current_info.csv", encoding='utf-8') as now_data:
            reader = csv.DictReader(now_data)
            while date < now:
            	# для поиска в таблице нужен другой формат даты, создаем его в этой переменной
                date_1 = date.strftime("%m/%d/%Y")
                date_1 = date_1.split('/')
                for i in range(len(date_1) - 1):
                    date_1[i] = date_1[i].lstrip('0')
                    dat = "/".join(date_1)
                dates.append(dat)
                date = date + datetime.timedelta(days=1)
            info = {}
            for row in reader:
                if row["Country/Region"] == location:
                    for d in dates:
                        if d not in info.keys():
                            info[d] = []
                            info[d].append(int(row[d[0:-2]]))
                        else:
                            info[d].append(int(row[d[0:-2]]))
            for data, value in info.items():
                data_set.append(sum(value))
        return dates, data_set

    @staticmethod
    def graphic_draw(shift: int, location: str, _param_coordinate="confirmed"):
        dates, data_set = Statistics.data(shift, location)
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
        #  вспомогательной сетки:
        ax.grid(which='minor',
                color='gray',
                linestyle=':')
        # название оси х
        plt.xlabel('days', fontsize=15)
        # имя оси Y
        plt.ylabel(_param_coordinate, fontsize=15)

        fig.set_figwidth(12)
        fig.set_figheight(8)

        plt.savefig('graphic')
        plt.clf()