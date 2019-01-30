import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlite3 import Cursor
import json
from re import compile


class Scraper:
    # if cursor is provided, data is saved, if not, data is returned
    def __init__(self, url: str, menu: str, yearMonth: str, c: Cursor = None):
        self.url = url
        self.menu = menu
        self.c = c

        # A yearMonth is a datetime formatted as .strftime('%Y-%m')
        self.yearMonth = yearMonth

    def go(self) -> dict:
        data = self.parse(self.fetch(self.url))
        if self.c:
            self.save(self.c, data)
        return data

    def fetch(self, url) -> str:
        params = {'adj': 0, 'current_month': f'{self.yearMonth}-01'}
        return requests.post(f'https://myschooldining.com/{url}/calendarMonth', params=params).text

    def parse(self, html) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        for i in [i for i in soup.find_all(class_="weekday") if i['class'] in [['weekday', 'month'], ['month', 'weekday']] and len(i['id']) > 4]:
            formattedDate = datetime.strptime(i['this_date'],'%m/%d/%y').strftime('%Y-%m-%d')
            data[formattedDate] = self.prettify(i)
        return data

    def prettify(self, soup) -> list:
        try:
            rawItems = soup.find(class_="menu-{}".format(self.menu)).findAll("span", class_=compile('month-(item|category|period)'))
            rawItems = [i for i in rawItems]

            last = None
            menuItems = []
            for i in rawItems:
                extractedText = self.extractText(i)
                if extractedText != last:
                    menuItems.append(extractedText)

                last = extractedText

        except AttributeError:
            menuItems = ['Information Not Found']


        return menuItems

    def extractText(self, ele) -> str:
        if 'month-category' in ele['class'] or 'month-period' in ele['class']:
            return '\n' + self.strip(ele.text)
        else:
            return self.strip(ele.text)

    def strip(self, text):
        return text.replace("\xa0", "").replace("\n", "").strip()

    def save(self, c: Cursor, data):
        menuItems = []

        for point in data:
            menuItems.append((point, json.dumps(data[point])))

        # if they already exist, there's a chance the menu has changed
        # (which has happened before), so it will override
        c.executemany(
            'INSERT OR REPLACE INTO menu VALUES (?,?)', menuItems)
        c.connection.commit()
