from abc import ABC, abstractmethod
from sqlite3 import Cursor
import urllib.parse

class BaseScraper(ABC):
    def __init__(self, base_url: str):
        '''
        The base scraper all sub-scrapers pull from

        base_url: base url of the service data is being pulled from. Used to build urls
        table_name: the sql table to store menu data in
        cursor: an sqlite3 cursor connected to the cache db
        '''
        self.base_url = base_url

    def build_url(self, resource: str):
        '''
        Takes a site resource and combines it with the base_url

        resource: the path after that comes after the base_url
        '''
        if not self.base_url.endswith('/') and not resource.startswith('/'):
            # If the base url doesn't end with a / and the path doesn't start with one,
            # then join them with a slash
            return self.base_url + '/' + resource
        elif self.base_url.endswith('/') and resource.startswith('/'):
            # If base url ends with / and path starts with one, remove a slash
            return self.base_url + resource[1:]
        else:
            # if this point reached, only one has a slash, so it's okay to join them
            return self.base_url + resource

    @abstractmethod
    def scrape(self):
        pass