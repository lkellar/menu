import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlite3 import Cursor
import json
import re
import threading

from menu.util import emailAdmin


class Scraper:
    # if cursor is provided, data is saved, if not, data is returned
    def __init__(self, url: str, menu: str, yearMonth: str, emailConfig: dict = None, c: Cursor = None):
        self.url = url
        self.menu = menu
        # SQLite Cursor
        self.c = c

        self.emailConfig = emailConfig

        # A yearMonth is a datetime formatted as .strftime('%Y-%m')
        self.yearMonth = yearMonth

    def go(self) -> dict:
        data = self.parse(self.fetch(self.url))
        # If there is a cursor, save data into the database
        if self.c:
            self.save(self.c, data)
        return data

    def fetch(self, url) -> str:
        # Setting params up to get current month
        params = {'adj': 0, 'current_month': f'{self.yearMonth}-01'}
        return requests.post(f'https://myschooldining.com/{url}/calendarMonth', params=params).text

    def parse(self, html) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        titles = self.fetchMenuTitles(soup)

        # If the chosen menu is not available AND email prefs were set,
        # start a separate thread to email the administrator
        if self.menu not in titles and self.emailConfig:
            t = threading.Thread(target=emailAdmin,
                                 args=(self.emailConfig, titles, self.menu))
            t.start()

        data = {}
        for i in [i for i in soup.find_all(class_="weekday") if i['class'] in [['weekday', 'month'], ['month', 'weekday']] and len(i['id']) > 4]:
            formattedDate = datetime.strptime(i['this_date'], '%m/%d/%y').strftime('%Y-%m-%d')

            if self.menu in titles:
                data[formattedDate] = self.prettify(i)
            else:
                # If the menu doesn't exist, the information we're looking for doesn't exist
                data[formattedDate] = ['Information Not Found']
        return data

    def prettify(self, soup) -> list:
        try:
            rawItems = soup.find(class_="menu-{}".format(self.menu)).findAll("span", class_=re.compile('month-(item|category|period)'))
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

    def fetchMenuTitles(self, soup) -> list:
        # taking the html from the site and getting all the available menus
        # in case the user selected one is unavailable
        titles = []
        r = re.compile('menu-([^location].*)')
        print(soup.find('div', class_="weekday month"))
        for i in soup.find('div', class_='weekday month').find('div', class_="content").find_all("div", class_="menu-location"):
            print(i['class'])
            titles.append(next(filter(r.match, i['class'])).replace('menu-', ''))

        return titles

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

