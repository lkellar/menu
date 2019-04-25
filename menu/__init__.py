from menu.app import app
import os, json
from menu.fetcher import Fetcher
from menu.util import monthlist_fast
from menu.scraper import Scraper
import sqlite3

def resetCache():
    # Can be used by a server admin to reset the cache
    # I personally have a cron run this function every morning at 9am ish
    currentDir = os.path.dirname(os.path.realpath(__file__))
    configPath = os.path.join(currentDir, '../config.json')
    with open(configPath, 'r') as f:
        config = json.load(f)
    config['cache'] = config['cache'].replace('$HERE', os.path.join(currentDir, '..'))
    fetch = Fetcher(config)
    with sqlite3.connect(config['cache']) as conn:
        c = conn.cursor()
        fetch.resetCache(c)
        c.close()

def historicalScrape(cache: str, url: str, menu: str, start: str,
                     end: str = None):
    if not end:
        end = start

    months = monthlist_fast((start, end))

    with sqlite3.connect(cache) as conn:
        c = conn.cursor()
        for i in months:
            Scraper(url, menu, i, None, c).go()