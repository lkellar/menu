import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Scraper:
    def __init__(self, url: str, menu: str, months: int = 0):
        self.url = url
        self.menu = menu
        nextMonth = datetime.today() + relativedelta(months=months)
        self.month = nextMonth.month
        self.year = nextMonth.year

    def go(self) -> dict:
        return self.parse(self.fetch(self.url))

    def fetch(self, url) -> str:
        params = {'adj': 0, 'current_month': '{}-{}-01'.format(self.year, self.month)}
        return requests.post('https://myschooldining.com/{}/calendarMonth'.format(url), params=params).text

    def parse(self, html) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        data = {}
        for i in [i for i in soup.find_all(class_="weekday") if i['class'] in [['weekday', 'month'], ['month', 'weekday']] and len(i['id']) > 4]:
            formattedDate = datetime.strptime(i['this_date'],'%m/%d/%y').strftime('%Y-%m-%d')
            data[formattedDate] = self.prettify(i)
        return data

    def prettify(self, soup) -> list:
        try:
            menuItems = soup.find(class_="menu-{}".format(self.menu)).findAll("span", class_="no-print")

            menuItems = [i for i in menuItems]

            menuItems = [self.extractText(i) for i in menuItems]

            headers = [i.replace('\n', '') for i in menuItems if i.startswith('\n')]

            for i in headers:
                menuItems.remove(i)
        except AttributeError:
            menuItems = ['Information Not Found']

        return menuItems

    def extractText(self, ele) -> str:
        if 'month-category' in ele['class']:
            return '\n' + self.strip(ele.text)
        else:
            return self.strip(ele.text)

    def strip(self, text):
        return text.replace("\xa0", "").replace("\n", "").strip()

