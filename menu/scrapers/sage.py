from menu.scrapers.base import BaseScraper
from sqlite3 import Cursor
from dataclasses import dataclass
from requests import Session
from datetime import timedelta, datetime, date

@dataclass
class SageConfig():
    '''
    A data class to standardize configs passed to SageScraper

    email: the email address used to login to Sage API
    password: password corresponding with the email address
    unit_id: the school unit id found in /findschool from the Sage API
    menu_id: the menu id to scrape. Found in /getmenus from the Sage API
    '''
    email: str
    password: str
    unit_id: int
    menu_id: int

class SageScraper(BaseScraper):
    def __init__(self, config: SageConfig, table_name: str, cursor: Cursor):
        '''
        Sets up a scraper conforming to BaseScraper

        config: SageConfig with info only relevant to SageScraper
        table_name: the sql table to store menu data in
        cursor: an sqlite3 cursor connected to the cache db
        '''
        self.config = config
        self.table_name = table_name
        self.cursor = cursor
        self.session = Session() 
        self.base_url = 'https://sagedining.com/rest/SageRest/v1/public/customerapp'
        super().__init__(self.base_url)

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

    def data_pull(self) -> dict:
        '''
        Calls the /datapull function as described in the SAGE_API.md

        Returns the API response
        '''
        return self.session.get(self.build_url('dataPull')).json()

    def get_menus(self, unit_id: int) -> dict:
        return self.session.get(self.build_url('getmenus'), params={'unitId': unit_id}).json()

    
class SageDateHandler:
    '''
    A dedicated class meant to deal with the oddities of Sage Date handling 
    without cluttering up the main Scraper class
    '''
    def __init__(self, cycle_length: int, menu_first_date: str):
        '''
        Initializes a SageDateHandler

        cycle_length: the number of weeks a Sage Menu runs. Found in /getmenus
        menu_first_date: the value of menuFirstDate of a menu found in /getmenus
        '''
        self.cycle_length = cycle_length
        # self.start_date is a date corresponding to the Sunday of the first week the Sage Menu offers
        self.start_date = self.parse_first_date(menu_first_date)
        
    @staticmethod
    def parse_first_date(menu_first_date: str) -> date:
        '''
        Inputs a date from Sage API, and returns the Sunday of that same week

        menu_first_date: the value of menuFirstDate of a menu found in /getmenus
        '''
        menu_first_date = datetime.strptime(menu_first_date, "%m/%d/%Y").date()

        # If the parsed date is not a Sunday (weekday 6), find the sunday of that week
        if menu_first_date.weekday() < 6:
            # Because sunday is the first day of the week in the Sage system, we always subtract
            # In python, Monday is the first day of the week, so we add one to the weekday value, then subtract
            return menu_first_date - timedelta(days=menu_first_date.weekday() + 1)

        # If the menu_first_date is already sunday, no need to alter it
        return menu_first_date

    def sage_to_date(self, week: int, day: int) -> date:
        '''
        Inputs a Sage date in Sage Format (week and day) and returns a date object

        week: the week number of the menu cycle
        day: the day of the provided week
        '''
        return self.start_date + timedelta(weeks=week) + timedelta(days=day)

    def date_to_sage(self, date: date) -> dict:
        '''
        Inputs a Date object and returns a Sage Date in (week, day) format via a dict

        date: a Date object
        '''
        if date < self.start_date:
            raise SageDateRangeError('Provided date is before menu start date')

        # difference in days between provided date and start date
        difference_days = (date - self.start_date).days

        difference_weeks = difference_days // 7

        # getting the remainder of days after a weeks division
        difference_days = difference_days % 7

        return {'week': difference_weeks, 'day': difference_days}

        
class SageDateRangeError(BaseException):
    '''
    An exception to be used when a Sage Date can't be processed
    '''
    def __init__(self, message):
        super().__init__(message)