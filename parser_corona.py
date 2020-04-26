import requests
import datetime
import csv

class Parser_coronavirus:
    def __init__(self, url_date = None, shift_date=0):
        if not url_date:
            now = datetime.datetime.today() - datetime.timedelta(days=shift_date)
            now = now.strftime('%m-%d-%Y')
            self.time = now.split('-')
            self.url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
                       'csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv'

    def write_data_corona(self):
        req = requests.get(self.url)
        if not req.ok:
            #если была введена больше ранняя дата
            for i in range(30):
                if not req.ok:
                    self.time[1] = int(self.time[1])
                    if self.time[1] <= 10:
                        self.time[1] = '0' + str(self.time[1] - 1)
                    else:
                        self.time[1] = str(self.time[1] - 1)
                    link = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{self.time[0]}-{self.time[1]}-{self.time[2]}.csv"
                    req = requests.get(link)
                else:
                    break
            return "Mistake occurred("
        with open("current_info.csv", "wb") as state_file:
            state_file.write(req.content)

    def find_top_five(self):
        with open("current_info.csv", 'r') as state_file:
            places, new_places, buffer, answer = list(), list(), list(), list()
            reader = csv.DictReader(state_file)
            for row in reader:
                if row[location]:
                    pair = [ row[location],
                             int(row[aspect]) ]
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

            for i in range(5):
                answer.append(new_places[len(new_places) - 1 - i][0] + " : " + str(new_places[len(new_places) - 1 - i][1]))
            return answer

