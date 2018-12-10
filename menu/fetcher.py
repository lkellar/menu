from datetime import datetime, timedelta
from menu.scraper import Scraper
import json
import sqlite3
from os import path

class Fetcher:
    def __init__(self, config):
        self.school = config['school']
        self.menu = config['menu']

        currentDir = path.dirname(path.realpath(__file__))

        self.conn = sqlite3.connect(path.join(currentDir, '../menu.sqlite3'))
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE IF NOT EXISTS menu
                                             (date text PRIMARY KEY UNIQUE, data text)''')

    def week(self, monday: datetime):
        friday = monday + timedelta(days=4)
        return self.prepAndGet(False, monday, friday)

    def fetchFromDatabase(self, start: str, end: str) -> dict:
        query = "SELECT * from menu where date BETWEEN ? and ?"
        data = self.c.execute(query, (start, end)).fetchall()

        # Formatting the data from the database into a lovely dictionary
        return {i[0]: json.loads(i[1]) for i in data}

    def validDate(self, start: str, end: str = None)-> bool:
        if end:
            query = "SELECT COUNT(*) from menu where date BETWEEN ? and ?"
            result = self.c.execute(query, (start, end)).fetchone()
        else:
            query = "SELECT COUNT(*) from menu where date is ?"
            result = self.c.execute(query, (start,)).fetchone()
        if result[0] > 0:
            return True
        return False

    def get(self, prettify: bool, start: str, end: str):
        menuData = self.fetchFromDatabase(start, end)
        if prettify:
            wordifyData = [self.wordify(menuData[i], i) for i in menuData]
            if len(wordifyData) == 1:
                wordifyData = wordifyData[0]
            return {"data": wordifyData}
        return menuData

    def prepAndGet(self, prettify: bool, start: datetime, end: datetime = None) -> dict:
        # if only start date is passed, set end as start date
        if not end:
            end = start

        currentMonth = datetime.today().month
        startIso = start.strftime('%Y-%m-%d')
        endIso = end.strftime('%Y-%m-%d')

        if self.validDate(startIso, endIso) > 0:
            return self.get(prettify, startIso, endIso)
        elif end.month == currentMonth + 1 or end.month - currentMonth == 11:
            if self.validDate(startIso, endIso) > 0:
                self.save(self.scrape(1))
                return self.get(startIso, endIso)
            else:
                return self.genError(start, end)
        elif start.month is not currentMonth:
            return self.genError(start, end)
        else:
            self.save(self.scrape(0))
            if self.validDate(startIso, endIso) > 0:
                return self.get(prettify, startIso, endIso)
            else:
                return self.genError(start, end)

    def genError(self, start: datetime, end: datetime) -> dict:
        date_list = [end - timedelta(days=x) for x in
                     range(0, (end - start).days)]
        return {i.strftime('%Y-%m-%d'):
                'The requested menu data is not available now'
                for i in date_list}

    def scrape(self, months: int = 0):
        return Scraper(self.school, self.menu, months).go()

    def resetCache(self):
        self.save(self.scrape())

    def save(self, data):
        menuItems = []

        for point in data:
            menuItems.append((point, json.dumps(data[point])))

        # if they already exist, there's a chance the menu has changed
        # (which has happened before), so it will override
        self.c.executemany(
            'INSERT OR REPLACE INTO menu VALUES (?,?)', menuItems)
        self.conn.commit()

    def wordify(self, menuData: list, date: str):
        date = datetime.strptime(date, '%Y-%m-%d')
        data = '\n'.join(menuData)
        return f'The menu for {date.strftime("%A, %B %d, %Y")}:\n{data}'
