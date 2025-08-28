import json
from dataclasses import dataclass
from datetime import timedelta, datetime, date
from requests import Session
from flask_sqlalchemy import SQLAlchemy
from menu.scrapers.base import BaseScraper
from menu.models import SageMenuItem

# A dict of that corresponds the dot attribute found in a menu item to the allergy colors
# it needs displayed
DOT_TO_COLORS = {1: ['red'], 2: ['yellow'], 3: ['green'], 4: ['green', 'yellow'],
                 5: ['yellow', 'red'], 6: ['green', 'yellow', 'red'], 7: ['green', 'red']}

# A list of all stations, in the correct order
STATION_TITLES = ['Stock Exchange', 'Improvisations', 'Classic Cuts Deli', 'Main Ingredient',
                  'Seasonings', 'Crossroads', 'Mangia!', 'Transit Fare', 'P.S.', 'Splashes',None,None,None,None,None,'FreeStyle',None,None,None,None,"Trattoria", "Ladle & Co."]

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

    def get_current_week(self) -> int:
        '''
        Gets the current date, and figures out what the current sage week is

        returns: current sage week
        '''
        current_date = date.today()
        sage_date = self.date_to_sage(current_date)

        return sage_date['week']

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
            date = (sunday + timedelta(days=i))
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
    def __init__(self, config: SageConfig, db: SQLAlchemy):
        '''
        Sets up a scraper conforming to BaseScraper

        config: SageConfig with info only relevant to SageScraper
        table_name: the sql table to store menu data in
        cursor: an sqlite3 cursor connected to the cache db
        '''
        self.config = config
        self.session = Session()
        self.db = db
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

        current_week = date_handler.get_current_week()

        # For all the weeks, run get_menu_items for that week and format the data
        for i in range(current_week, int(menu['cycleLength'])):
            raw_data = self.get_menu_items(menu['id'], i)
            if raw_data:
                menu_items += self.format_data_for_storage(raw_data, date_handler)

        self.save(menu_items)


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

    def get_menu_items(self, menu_id: int, week: int) -> list:
        '''
        Takes a Sage Week number and returns the menu data for that week with iso formatted dates

        menu_id: the id of the menu to get data for
        week: the week to get menu data for

        returns: an array of menu items from the server. the menu items match the
        example in the docs
        '''
        payload = {'id': menu_id, 'week': week}
        # Hit the /getMenusItems API
        response = self.session.post(self.build_url('getmenuitems'), json=payload).json()

        if response['error']:
            # If the api raises an error, we raise it as well
            raise SageAPIError(response['reason'])

        return response['items']

    @staticmethod
    def format_data_for_storage(menu_data: list, date_handler: SageDateHandler) -> list:
        # Grabbing the week off the first menu item to gen a date list
        # All menu items should have the same week
        week = int(menu_data[0]['week'])

        # Fetching an array of the dates in that week: ['2019-08-18, ...]
        # so we can match up the sage date in the item to a real date
        week_dates = date_handler.generate_date_list(week)

        formatted_menu_items = []

        for i in menu_data:
            # Getting the real date determined by the weekday on item for use in the SageMenuTiem
            date = week_dates[int(i['day'])]

            # This blob here turns the json response into a model we can put in the db
            # As it satisfies the named parameters, it removes them from the item object,
            # so all the remaining item object key/values can be put into a misc object,
            # if they are to be needed down the road
            formatted_item = {'id': int(i.pop('id')), 'menu_id': int(i.pop('menuId')),
                              'recipe_id': int(i.pop('recipeId')), 'day': int(i.pop('day')),
                              'week': int(i.pop('week')), 'meal': int(i.pop('meal')),
                              'station': int(i.pop('station')), 'name': i.pop('name'),
                              'allergens': json.dumps(i.pop('allergens')), 'date': date,
                              'card': int(i.pop('card')), 'dot': int(i.pop('dot')),
                              'misc': json.dumps(i)}

            formatted_menu_items.append(formatted_item)

        return formatted_menu_items

    def save(self, menu_data: list):
        '''
        Takes menu data and stores it in the db using the provided SQLAlchemy Instance

        menu_data: list: A list of properly formatted SageMenuItems
        db: SQLAlchemy Instance
        '''

        # get all unique dates in the menu_data
        unique_dates = {i['date'] for i in menu_data}

        # then, with those unique dates, remove all menu_data that has the same date as the data
        # we are about to insert
        # this is done because sometimes sage changes their menus, and if you leave in existing
        # entries, you'll have extra entries for a given day that aren't accurate
        delete_query = SageMenuItem.delete().where(SageMenuItem.c.date.in_(unique_dates))

        self.db.session.execute(delete_query)
        self.db.session.commit()

        # creates an inserter object so duplicates replace their predecessor
        inserter = SageMenuItem.insert().prefix_with('OR REPLACE')
        self.db.session.execute(inserter, menu_data)
        self.db.session.commit()


class SageDateRangeError(BaseException):
    '''
    An exception to be used when a Sage Date can't be processed
    '''


class SageAPIError(BaseException):
    '''
    An exception to be used when the Sage API has an error
    '''
