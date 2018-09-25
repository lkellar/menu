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
            data.update(self.get(False, date))
        return data

    def get(self, prettify: bool, date: datetime):
        if isfile(self.cache):
            with io.open(self.cache, "r", encoding='utf8') as f:
                try:
                    cache = json.load(f)
                except json.decoder.JSONDecodeError:
                    Scraper(self.cache, self.school, self.menu).go()
                    return self.get(prettify, date)

            isoDate = date.strftime('%Y-%m-%d')
            if isoDate in cache:
                menuData = cache[isoDate]
                if prettify:
                     menuData = {"data": self.wordify(menuData, date)}
                else:
                    menuData = {isoDate: menuData}
                return menuData
            elif date.month is not datetime.today().month:
                return {isoDate: 'Next month\'s menu is not available now'}
            else:
                Scraper(self.cache, self.school, self.menu).go()
                return self.get(prettify, date)
        else:
            Scraper(self.cache, self.school, self.menu).go()
            return self.get(prettify, date)

    def wordify(self, menuData, date):
        return '''The menu for {}:\n{}'''.format(date.strftime('%A, %B %d, %Y'), '\n'.join(menuData))