from datetime import datetime, timedelta
from menu.scraper import Scraper
from menu.util import genNumber
import json
import sqlite3
from sqlite3 import Cursor
from dateutil.relativedelta import relativedelta
from calendar import monthrange

class Fetcher:
    def __init__(self, config: dict):
        self.school = config['school']
        self.menu = config['menu']

        with sqlite3.connect(config['cache']) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS menu
                                                 (date text PRIMARY KEY UNIQUE, data text)''')

    def week(self, c: Cursor, monday: datetime):
        friday = monday + timedelta(days=4)
        return self.prepAndGet(c, False, monday, friday)

    def fetchFromDatabase(self, c: Cursor, start: str, end: str) -> dict:
        base = datetime.strptime(end, '%Y-%m-%d')
        floor = datetime.strptime(start, '%Y-%m-%d')
        diff = (base - floor).days
        date_list = [(base - timedelta(days=x)).strftime('%Y-%m-%d') for x in
                     range(0, diff+1)]
        counts = self.chickenCount(date_list, c)

        query = "SELECT * from menu where date BETWEEN ? and ?"
        data = c.execute(query, (start, end)).fetchall()

        # Formatting the data from the database into a lovely dictionary
        return {i[0]: {'menu': json.loads(i[1]), 'chicken': {'count': counts[i[0]], 'positive': self.chickenPositive(i[1])}} for i in data}

    def chickenPositive(self, data: str) -> bool:
        if 'chicken' in data.lower():
            return True
        return False

    def chickenCount(self, dates: list, c: Cursor) -> dict:
        query = "SELECT COUNT(*) FROM menu WHERE data LIKE '%chicken%' AND date BETWEEN  '%' AND ?"
        count = {}
        for i in dates:
            count[i] = c.execute(query, (i,)).fetchone()[0]

        return count

    def validDate(self, c: Cursor, start: str, end: str = None)-> bool:
        if end:
            query = "SELECT COUNT(*) from menu where date BETWEEN ? and ?"
            result = c.execute(query, (start, end)).fetchone()
        else:
            query = "SELECT COUNT(*) from menu where date is ?"
            result = c.execute(query, (start,)).fetchone()
        if result[0] > 0:
            return True
        return False

    def get(self, c: Cursor, prettify: bool, start: str, end: str):
        menuData = self.fetchFromDatabase(c, start, end)
        if prettify:
            wordifyData = [self.wordify(menuData[i], i) for i in menuData]
            if len(wordifyData) == 1:
                wordifyData = wordifyData[0]
            return {"data": wordifyData}
        return menuData

    def prepAndGet(self, c: Cursor, prettify: bool, start: datetime, end: datetime = None) -> dict:
        # if only start date is passed, set end as start date
        if not end:
            end = start

        print(start)

        currentMonth = datetime.today().month
        startIso = start.strftime('%Y-%m-%d')
        endIso = end.strftime('%Y-%m-%d')

        if self.validDate(c, startIso, endIso) > 0:
            return self.get(c, prettify, startIso, endIso)
        elif end.month == currentMonth + 1 or end.month - currentMonth == 11:
            if self.validDate(c, startIso, endIso) > 0:
                self.scrape(1, c)
                return self.get(startIso, endIso)
            else:
                return self.genError(start, end)
        elif start.month is not currentMonth:
            return self.genError(start, end)
        else:
            self.scrape(0, c)
            if self.validDate(c, startIso, endIso) > 0:
                return self.get(prettify, startIso, endIso)
            else:
                return self.genError(start, end)

    def genError(self, start: datetime, end: datetime) -> dict:
        date_list = [end - timedelta(days=x) for x in
                     range(0, (end - start).days)]
        return {i.strftime('%Y-%m-%d'):
                'The requested menu data is not available now'
                for i in date_list}

    def scrape(self, months: int = 0, c: Cursor = None):
        nextMonth = datetime.today() + relativedelta(months=months)
        yearMonth = nextMonth.strftime('%Y-%m')
        return Scraper(self.school, self.menu, yearMonth, c).go()

    def resetCache(self, c: Cursor):
        self.scrape(0, c)
        today = datetime.today()
        days = monthrange(today.year, today.month)[1]
        if days - today.day < 8:
            self.scrape(1, c)

    def wordify(self, menuData: dict, date: str):
        date = datetime.strptime(date, '%Y-%m-%d')
        data = '\n'.join(menuData['menu'])
        if menuData['chicken']['positive']:
            data += f'\n\nThis is the {genNumber(menuData["chicken"]["count"])} time we\'ve had chicken this year.'
        return f'The menu for {date.strftime("%A, %B %d, %Y")}:\n{data}'
