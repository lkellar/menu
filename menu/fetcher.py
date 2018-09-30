from datetime import datetime, timedelta
import json
from menu.scraper import Scraper
import io
from os.path import isfile

class Fetcher:
    def __init__(self, config):
        self.school = config['school']
        self.menu = config['menu']
        self.cache = config['cache']

    def week(self, monday: datetime):
        data = {}
        for i in range(0,5):
            date = monday + timedelta(days=i)
            menuData = self.get(False, date)
            if len(menuData[date.strftime('%Y-%m-%d')]) > 0:
                data.update(menuData)
        return data

    def get(self, prettify: bool, date: datetime):
        if isfile(self.cache):
            with io.open(self.cache, "r", encoding='utf8') as f:
                try:
                    cache = json.load(f)
                except json.decoder.JSONDecodeError:
                    self.save(self.scrape())
                    return self.get(prettify, date)

            isoDate = date.strftime('%Y-%m-%d')
            currentMonth = datetime.today().month
            if isoDate in cache:
                menuData = cache[isoDate]
                if prettify:
                     menuData = {"data": self.wordify(menuData, date)}
                else:
                    menuData = {isoDate: menuData}
                return menuData
            elif date.month == currentMonth + 1:
                next = self.scrape(1)
                self.save({**cache, **next})
                return self.get(prettify, date)
            elif date.month is not currentMonth:
                return {isoDate: 'The requested menu data is not available now'}
            else:
                self.save(self.scrape())
                return self.get(prettify, date)
        else:
            self.save(self.scrape())
            return self.get(prettify, date)

    def scrape(self, months: int = 0):
        return Scraper(self.school, self.menu, months).go()

    def save(self, data):
        with io.open(self.cache, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False)

    def wordify(self, menuData, date):
        return '''The menu for {}:\n{}'''.format(date.strftime('%A, %B %d, %Y'), '\n'.join(menuData))