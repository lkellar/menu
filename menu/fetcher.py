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
        self.config = config

        with sqlite3.connect(config['cache']) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS menu
                                                 (date text PRIMARY KEY UNIQUE, data text)''')

    def week(self, c: Cursor, monday: datetime):
        # Input: The monday of a week
        # Returns menu data for the whole school week
        friday = monday + timedelta(days=4)
        return self.prepAndGet(c, False, monday, friday)

    def fetchFromDatabase(self, c: Cursor, start: str, end: str) -> dict:
        # Getting all menu data required from Database
        query = "SELECT * from menu where date BETWEEN ? and ?"
        data = c.execute(query, (start, end)).fetchall()

        # Formatting the data from the database into a lovely dictionary
        return {i[0]: {'menu': json.loads(i[1])} for i in data}

    def validDate(self, c: Cursor, start: str, end: str = None) -> bool:
        # Checks if the date provided is actually in the database
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
        # Takes start and end dates, and fetches from the data base
        menuData = self.fetchFromDatabase(c, start, end)
        if prettify:
            wordifyData = [self.wordify(menuData[i], i) for i in menuData]
            if len(wordifyData) == 1:
                wordifyData = wordifyData[0]
            return {"data": wordifyData}
        return menuData

    def prepAndGet(self, c: Cursor, prettify: bool, start: datetime, end: datetime = None) -> dict:
        # This function is kind of the screener function, and if the parameters passed are valid, they move on
        # if only start date is passed, set end as start date
        if not end:
            end = start

        currentMonth = datetime.today().month
        startIso = start.strftime('%Y-%m-%d')
        endIso = end.strftime('%Y-%m-%d')

        # if valid date, get data from database and return it
        if self.validDate(c, startIso, endIso) > 0:
            return self.get(c, prettify, startIso, endIso)

        # if not valid date, but the date provided is in the next date,
        # scrape the data for next month
        elif end.month == currentMonth + 1 or end.month - currentMonth == 11:
            if self.validDate(c, startIso, endIso) > 0:
                self.scrape(1, c)
                return self.get(c, prettify, startIso, endIso)
            else:
                return self.genError(start, end)

        # If the starting month isn't the current month (or next month), throw an error
        elif start.month is not currentMonth:
            return self.genError(start, end)
        # throw an error
        else:
            return self.genError(start, end)

    def genError(self, start: datetime, end: datetime) -> dict:
        # An error message that works with the site and the API
        if end == start:
            date_list = [start]
        else:
            date_list = [end - timedelta(days=x) for x in
                         range(0, (end - start).days)]
        return {i.strftime('%Y-%m-%d'):
                'The requested menu data is not available now'
                for i in date_list}

    def scrape(self, months: int = 0, c: Cursor = None, email: bool = True):
        # The email variable will email the administrator about missing menus if true

        # preps the scraper and scrapes, passes a cursor so data is saves
        nextMonth = datetime.today() + relativedelta(months=months)
        yearMonth = nextMonth.strftime('%Y-%m')
        # Scrapes data and puts in the email configuration data if it exists
        return Scraper(self.school, self.menu, yearMonth, self.config['email'] if 'email' in self.config and email else None, c).go()

    def resetCache(self, c: Cursor):
        # Overwrites cache to update menu listings
        # Used by the resetCache function in the __init__.py
        self.scrape(0, c)
        today = datetime.today()
        days = monthrange(today.year, today.month)[1]
        if days - today.day < 8:
            # We set email to false, because if menus are missing, the admin wouldn've
            # been alerted during the previous scrape
            self.scrape(1, c, email=False)

    def wordify(self, menuData: dict, date: str):
        # Takes JSON and formats it for the Siri Shortcut, or any other
        # user presentable text
        date = datetime.strptime(date, '%Y-%m-%d')
        data = '\n'.join(menuData['menu'])
        return f'The menu for {date.strftime("%A, %B %d, %Y")}:\n{data}'
