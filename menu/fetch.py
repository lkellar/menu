from datetime import timedelta, datetime
from itertools import groupby
from flask_sqlalchemy import SQLAlchemy
import pytz
from menu.models import SageMenuItem
from menu.scrapers.sage import STATION_TITLES

class Fetcher:
    '''
    A class to handle all the menu data fetching for the app
    '''
    def __init__(self, db: SQLAlchemy, timezone: str, meal_titles: list):
        # Fetches the db from the models file, initalizes the database, and creates tables
        self.db = db
        self.meal_titles = meal_titles

        self.timezone = pytz.timezone(timezone)

    def get_default_date(self) -> datetime.date:
        '''
        Gets today's date if before 1pm in timezone, or tomorrow's if after
        '''

        # Get the current date/time in the provided timezone
        start = datetime.now(self.timezone)

        # If it's after lunch time (1pm or after), go ahead and start with the following day
        # maybe the end time should be configurable
        if start.hour >= 13:
            start += timedelta(days=1)

        return start.date()

    def fetch_valid_dates(self, days: int, offset: int, descending: bool = False,
                          start: datetime.date = None) -> list:
        '''
        Accepts a number of dates, then returns the next x valid days with menu data.

        Params:
        days int: amount of days to fetch
        offset int: offset, so days = 5 and offset = 5 would get you the 6-10th available dates.
        descending
        start datetime.date: the date to start counting on (inclusive)
            - (optional): uses today as default (or tomorrow, if after 1pm) as start

        Returns, a list of dates
        '''

        if not start:
            start = self.get_default_date()

        if descending:
            dates = self.db.session.query(SageMenuItem.c.date).distinct().filter(
                SageMenuItem.c.date <= start).order_by(SageMenuItem.c.date.desc()).limit(
                    days+abs(offset)).all()
        else:
            # The statement below queries for all distinct date values, filters to get only ones
            # after the start, orders them in ascending order, sets a limit equalling the days param
            dates = self.db.session.query(SageMenuItem.c.date).distinct().filter(
                SageMenuItem.c.date >= start).order_by(SageMenuItem.c.date).limit(
                    days+abs(offset)).all()

        dates = dates[abs(offset):]

        # Each instance in the list is a tuple of the date in 1st position, and nothing in 2nd
        return [i[0] for i in dates]


    def fetch_days(self, days: int, offset: int = 0, start: datetime.date = None) -> dict:
        '''
        Accepts day count and optional start date and returns menu items grouped by day, meal, and
        station
        '''
        if not start:
            start = self.get_default_date()

        if offset != 0:
            start = self.fetch_valid_dates(1, offset, descending=bool(offset < 0), start=start)
            if start:
                start = start[0]
            else:
                return {}

        # Gets the end date by finding 1 valid day, with offset days - 1, which gives the next valid
        # date, x days in advance
        end = self.fetch_valid_dates(1, abs(days)-1, descending=bool(days < 0), start=start)

        if end:
            end = end[0]

        if not end:
            if days > 0:
                # if a valid enddate is not found after the requested amount of days
                # return everything after the start (which will be less than requested)
                response = self.db.session.query(SageMenuItem).filter(
                    SageMenuItem.c.date >= start).all()
            else:
                # do the same as above, but go IN REVERSE
                response = self.db.session.query(SageMenuItem).filter(
                    SageMenuItem.c.date <= start).all()
        elif days > 0:
            # query the db for all items between start and end dates
            response = self.db.session.query(SageMenuItem).filter(
                SageMenuItem.c.date.between(start, end)).all()
        else:
            # query the db for all items between "end" and "start" dates
            response = self.db.session.query(SageMenuItem).filter(
                SageMenuItem.c.date.between(end, start)).all()

        return self.process_response(response)

    @staticmethod
    def process_response(response) -> dict:
        # sort the responses by the date attribute so they can be sorted
        response = sorted([i._asdict() for i in response], key=lambda k: k['date'])

        # group the menu items by their date key
        grouped_response = {}
        # Not using the group_by_key function because in this case, we need
        # to turn the key from a datetime to a str when turning it into a dict.
        for k, g in groupby(response, key=lambda k: k['date']):
            grouped_response[k.strftime('%Y-%m-%d')] = list(g)

        # iterate through each day of the grouped days
        for key, value in grouped_response.items():
            # for each day, group the menu items by meal
            grouped_value = group_by_key(value, 'meal')

            # iterate through the meals
            for sub_key, sub_value in grouped_value.items():
                # for each meal, group the menu items by station
                grouped_value[sub_key] = group_by_key(sub_value, 'station')

            grouped_response[key] = grouped_value

        return grouped_response

    def wordify(self) -> str:
        '''
        Gets the current menu data for today (or tomorrow if it's after lunch time) and makes it
        human readable

        returns: str, A human readable representation of the menu
        '''
        # Fetch menu data, and get the first item in the list, because we are requesting only one
        # day's worth of data
        date, menu_data = list(self.fetch_days(1).items())[0]

        date = datetime.strptime(date, '%Y-%m-%d')

        response = f'The menu for {date.strftime("%A, %B %d, %Y")}'

        for meal, meal_value in menu_data.items():
            response += f'\n\n{self.meal_titles[int(meal)]}'
            for station, station_value in meal_value.items():
                response += f'\n\n{STATION_TITLES[int(station)]}'
                for menu_item in station_value:
                    response += f'\n{menu_item["name"].replace("&amp;", "&")}'

        return {"response": response}


def group_by_key(data: list, key: str) -> dict:
    '''
    Takes a list of dicts, groups the dicts into 'buckets' determined by a key in the dict,
    then returns the bucket.

    data: list, A list of dicts
    key: str, A key that every dict in data must have, sorts by this key
    '''
    # Sort the data for the groupby function
    sorted_data = sorted(data, key=lambda k: k[key])

    grouped_data = {}
    # iterate through the groupby iterator, and add to a dictionary
    for k, g in groupby(sorted_data, key=lambda k: k[key]):
        grouped_data[str(k)] = list(g)

    return grouped_data
