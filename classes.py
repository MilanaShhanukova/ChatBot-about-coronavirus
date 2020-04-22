import csv
import requests
import datetime


# Необходимые функции для команды /corona_stats
# Скачиваем последний возможный файл с гитхаба и возвращаем часть ответного сообщения
class Calculator:
    def __init__(self):
        pass

    @staticmethod
    def download_actual_file(shift_date: int):
        answer = list()
        now = datetime.datetime.today() - datetime.timedelta(days=shift_date)
        now = now.strftime("%m/%d/%Y")
        now = now.split('/')
        link = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/\
        csse_covid_19_daily_reports/{now[0]}-{now[1]}-{now[2]}.csv"
        r = requests.get(link)
        if r.status_code == 200:
            answer.append("Информация о вирусе на сегодня:")
        # Если нет информации на сегодня, будет взята информация за вчера
        else:
            while not r.status_code == 200:
                now[1] = int(now[1])
                if now[1] <= 10:
                    now[1] = '0' + str(now[1] - 1)
                else:
                    now[1] = str(now[1] - 1)
                link = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/\
                csse_covid_19_data/csse_covid_19_daily_reports/{now[0]}-{now[1]}-{now[2]}.csv"
                r = requests.get(link)
            answer.append(f"Информация на сегодня пока нет. Последние данные на {'/'.join(now)} о вирусе:")
        # Скачиваем файл
        with open("current_info.csv", 'w', encoding='utf-8') as csv_file:
            csv_file.writelines(r.text)
        return answer

    # Получив местоположение и критерий, вытаскиваем нужную информацию в ответное сообщение answer
    # через буферный словарь Provinces
    @staticmethod
    def get_necessary_corona_info(location: str, aspect: str, answer: list):
        # Getting information
        with open("current_info.csv", 'r') as csv_file:
            places = list()
            new_places = list()
            buffer = list()
            reader = csv.DictReader(csv_file)
            # Append number of infected people in provinces
            for row in reader:
                if row[location]:
                    pair = [row[location], int(row[aspect])]
                    places.append(pair)
            for el in places:
                if el[0] not in buffer:
                    buffer.append(el[0])
                    new_places.append(el)
                else:
                    for pair in new_places:
                        if pair[0] == el[0]:
                            pair[1] += el[1]
                            break
            new_places.sort(key=lambda target: target[1])
            # Creating an answer
            for i in range(5):
                answer.append(new_places[len(new_places) - 1 - i][0] + " : " + str(new_places[len(new_places) - 1 - i][1]))

    @staticmethod
    def get_dynamics_info(target_country: str, shift_date: int):
        answer = Calculator.download_actual_file(shift_date)
        answer = []
        with open("current_info.csv", "r") as csv_file:
            reader = csv.DictReader(csv_file)
            places = []
            new_places = []
            buffer = []
            for row in reader:
                el = [
                    row["Country_Region"],
                    int(row["Confirmed"]),
                    int(row["Deaths"]),
                    int(row["Recovered"]),
                    int(row["Active"])]
                places.append(el)
            for country in places:
                if target_country == country[0]:
                    for el in places:
                        if el[0] not in buffer:
                            buffer.append(el[0])
                            new_places.append(el)
                        else:
                            for row in new_places:
                                if row[0] == el[0]:
                                    row[1] += el[1]
                                    row[2] += el[2]
                                    row[3] += el[3]
                                    row[4] += el[4]
                                    break
                    return new_places
