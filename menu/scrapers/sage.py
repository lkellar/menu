from sqlite3 import Cursor
from dataclasses import dataclass
from datetime import timedelta, datetime, date
from requests import Session
from menu.scrapers.base import BaseScraper

@dataclass
class SageConfig:
    '''
    A data class to standardize configs passed to SageScraper

    email str: the email address used to login to Sage API
    password str: password corresponding with the email address
    unit_id int: the school unit id found in /findschool from the Sage API
    menu_id int: the menu id to scrape. Found in /getmenus from the Sage API
    '''
    email: str
    password: str
    unit_id: int
    menu_id: int

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
        # self.start_date is a date corresponding to the Sunday of the
        #  first week the Sage Menu offers
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
            # In python, Monday is the first day of the week,
            # so we add one to the weekday value, then subtract
            return menu_first_date - timedelta(days=menu_first_date.weekday() + 1)

        # If the menu_first_date is already sunday, no need to alter it
        return menu_first_date

    def generate_date_list(self, week: int) -> list:
        '''
        Input a week number, and return an array that corresponds the weekday
        (or the array position) to the date

        week: the week number to use

        response example: ['2019-08-18', '2019-08-19', ...]
        '''
        date_list = []
        sunday = self.sage_to_date(week, 0)
        for i in range(0, 7):
            date = (sunday + timedelta(days=i)).strftime('%Y-%m-%d')
            date_list.append(date)

        return date_list


    def sage_to_date(self, week: int, day: int) -> date:
        '''
        Inputs a Sage date in Sage Format (week and day) and returns a date object

        week: the week number of the menu cycle
        day: the day of the provided week
        '''
        return self.start_date + timedelta(weeks=week) + timedelta(days=day)

    def date_to_sage(self, input_date: date) -> dict:
        '''
        Inputs a Date object and returns a Sage Date in (week, day) format via a dict

        date: a Date object
        '''
        if input_date < self.start_date:
            raise SageDateRangeError('Provided date is before menu start date')

        # difference in days between provided date and start date
        difference_days = (input_date - self.start_date).days

        difference_weeks = difference_days // 7

        # getting the remainder of days after a weeks division
        difference_days = difference_days % 7

        return {'week': difference_weeks, 'day': difference_days}


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
        self.session.headers.update({'Authorization': f'Bearer {access_token}'})

        # Fetch information about the menu to scrape
        menu = self.get_menu(self.config.unit_id, self.config.menu_id)

        # create a date_handler for the get_menu_items to use
        date_handler = SageDateHandler(int(menu['cycleLength']), menu['menuFirstDate'])

        menu_items = []

        # For all the weeks, run get_menu_items for that week
        # TODO don't let it scrape past data
        for i in range(0, int(menu['cycleLength'])):
            menu_items += self.get_menu_items(menu['id'], i, date_handler)


    def login(self, email: str, password: str) -> str:
        '''
        Logs into Sage API and returns access token

        email: email to login to Sage API with
        password: password corresponding to provided email
        '''
        payload = {'grant': 'password'}
        response = self.session.post(self.build_url('login'),
                                     json=payload, auth=(email, password)).json()
        access_token = response['credentials']['accessToken']
        return access_token

    def data_pull(self) -> dict:
        '''
        Calls the /datapull function as described in the SAGE_API.md

        Returns the API response
        '''
        return self.session.get(self.build_url('dataPull')).json()

    def get_menu(self, unit_id: int, menu_id: int) -> dict:
        '''
        Inputs a school unit_id and menu_id, and returns a menu object in dictionary form.

        The object returned is one member of the 'menus' array found in the response of /getmenus
        '''
        # Hit the API for provided school and get data for our requested menu
        menus_response = self.session.get(
            self.build_url('getmenus'), params={'unitId': unit_id}).json()

        if menus_response['error']:
            # If the api raises an error, we raise it as well
            raise SageAPIError(menus_response['reason'])

        # turn the array into a dictionary with the menu id as key
        menus = {int(i['id']): i for i in menus_response['menus']}

        if not menu_id in menus:
            raise SageAPIError('Menu ID not Found!')

        return menus[menu_id]

    def get_menu_items(self, menu_id: int, week: int, date_handler: SageDateHandler):
        '''
        Takes a Sage Week number and returns the menu data for that week with iso formatted dates

        menu_id: the id of the menu to get data for
        week: the week to get menu data for

        returns: a dict with a date in YYYY-MM-DD format as a key,
            and an array of food item dicts as the value
        '''
        payload = {'id': menu_id, 'week': week}
        # Hit the /getMenusItems API
        response = self.session.post(self.build_url('getmenuitems'), json=payload).json()

        if response['error']:
            # If the api raises an error, we raise it as well
            raise SageAPIError(response['reason'])

        # Fetching an array of the dates in that week: ['2019-08-18, ...]
        # so we can match up the sage date in the item to a real date
        week_dates = date_handler.generate_date_list(week)

        menu_items = []

        for item in response['items']:
            date = week_dates[int(item['day'])]
            item['date'] = date
            menu_items.append(item)

        return menu_items


class SageDateRangeError(BaseException):
    '''
    An exception to be used when a Sage Date can't be processed
    '''


class SageAPIError(BaseException):
    '''
    An exception to be used when the Sage API has an error
    '''
