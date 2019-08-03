from menu.scrapers.base import BaseScraper
from sqlite3 import Cursor
from dataclasses import dataclass
from requests import Session

@dataclass
class SageConfig():
    '''
    A data class to standardize configs passed to SageScraper

    email: the email address used to login to Sage API
    password: password corresponding with the email address
    '''
    email: str
    password: str

class SageScraper(BaseScraper):
    def __init__(self, config: SageConfig, menu: int, table_name: str, cursor: Cursor):
        '''
        Sets up a scraper conforming to BaseScraper

        config: SageConfig with info only relevant to SageScraper
        menu: the menu id to scrape. Sage Menu IDs are numbers
        table_name: the sql table to store menu data in
        cursor: an sqlite3 cursor connected to the cache db
        '''
        self.config = config
        self.menu = menu
        self.table_name = table_name
        self.cursor = cursor
        self.session = Session() 
        self.base_url = 'https://sagedining.com/rest/SageRest/v1/public/customerapp'
        super().__init__(self.base_url, self.menu)

    def scrape(self):
        '''
        Main controller for scraping data.
        
        Calls subfunctions to wrap it all together
        '''
        # Fetch the access token by logging in, and add it to the session
        access_token = self.login(self.config.email, self.config.password)
        self.session.headers.update({'Authentication': f'Bearer {access_token}'})

    def login(self, email: str, password: str) -> str:
        '''
        Logs into Sage API and returns access token

        email: email to login to Sage API with
        password: password corresponding to provided email
        '''
        response = self.session.post(self.build_url('login'), auth=(email, password)).json()
        access_token = response['credentials']['accessToken']
        return access_token

    