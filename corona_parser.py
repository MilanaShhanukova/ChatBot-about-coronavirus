from bs4 import BeautifulSoup
import requests
import csv


URL = "https://coronavirus-monitor.info/"
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/\
80.0.3987.132 YaBrowser/20.3.1.195 Yowser/2.5 Safari/537.36', 'accept': '*/*'}


class CoronaParser:
    TABLE = ""
    CONTENT = ""
    HEADERS = list()

    def __init__(self, html):
        self.html = html

    def start_parse(self):
        self.go_to_target_page()
        self.find_the_target_table()
        self.find_headers_for_csv_file()

    def go_to_target_page(self):
        self.CONTENT = BeautifulSoup(self.html, 'html.parser')

    def find_the_target_table(self):
        self.TABLE = self.CONTENT.find_all("div", class_="flex-table")[1:82]

    def find_headers_for_csv_file(self):
        self.HEADERS = self.CONTENT.find("div", class_="flex-table").text.split('\n')[1:-1]

    def collecting_data(self):
        with open("russian_data.csv", 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.HEADERS)
            writer.writeheader()
            for div in self.TABLE:
                div_data = div.find_all("div")
                row = {
                    self.HEADERS[0]: div_data[0].get_text(),
                    self.HEADERS[1]: div_data[1].get_text(),
                    self.HEADERS[2]: div_data[2].get_text(),
                    self.HEADERS[3]: div_data[3].get_text()}
                writer.writerow(row)


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code == 200:
        return r.text
    else:
        print("ERROR")
        return


def parse():
    html = get_html(URL)
    Parser = CoronaParser(html)
    Parser.start_parse()
    Parser.collecting_data()


parse()