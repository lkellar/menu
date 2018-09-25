import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import io

class Scraper:
    def __init__(self, saveLoc: str, url: str, menu: str):
        self.saveLoc = saveLoc
        self.url = url
        self.menu = menu

    def go(self):
        data = self.parse(self.fetch(self.url))
        self.save(self.saveLoc, data)

    def fetch(self, url) -> str:
        return requests.get('https://myschooldining.com/{}'.format(url)).text

    def parse(self, html) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        for i in [i for i in soup.find_all(class_="weekday") if i['class'] in [['weekday', 'month'], ['month', 'weekday']] and len(i['id']) > 4]:
            formattedDate = datetime.strptime(i['this_date'],'%m/%d/%y').strftime('%Y-%m-%d')
            data[formattedDate] = self.prettify(i)
        return data

    def prettify(self, soup) -> list:
        menuItems = soup.find(class_="menu-{}".format(self.menu)).findAll("span", class_="no-print")

        menuItems = [i for i in menuItems]

        menuItems = [self.extractText(i) for i in menuItems]

        headers = [i.replace('\n', '') for i in menuItems if i.startswith('\n')]

        for i in headers:
            menuItems.remove(i)

        return menuItems

    def extractText(self, ele) -> str:
        if 'month-category' in ele['class']:
            return '\n' + self.strip(ele.text)
        else:
            return self.strip(ele.text)

    def strip(self, text):
        return text.replace("\xa0", "").replace("\n", "").strip()

    def save(self, saveLoc, data):
        with io.open(saveLoc, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False)
