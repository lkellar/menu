from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
import pytz
from menu.models import SageMenuItem

class Fetcher:
    '''
    A class to handle all the menu data fetching for the app
    '''
    def __init__(self, db: SQLAlchemy, timezone: str):
        # Fetches the db from the models file, initalizes the database, and creates tables
        self.db = db

        self.timezone = pytz.timezone(timezone)

    def fetch_days(self, days: int, start: datetime.date = None):
        if not start:
            # Get the current date/time in the provided timezone
            start = datetime.now(self.timezone)

            # If it's after lunch time (1pm or after), go ahead and start with the following day
            if start.hour >= 13:
                start += timedelta(days=1)

            start = start.date()

        # Query the db to get the next x dates that have menu items accounted for where x is 
        # the days param
        # The statement below queries for all distinct date values, filters to get only ones after
        # the start, orders them in ascending order, sets a limit equalling the days param,
        # then getting the last date in the response
        end = self.db.session.query(SageMenuItem.c.date).distinct().filter(
            SageMenuItem.c.date >= start).order_by(SageMenuItem.c.date).limit(days).all()[-1][0]

        # query the db for all items between start and end dates
        response = self.db.session.query(SageMenuItem).filter(
            SageMenuItem.c.date.between(start, end)).group_by(SageMenuItem.c.date).all()

        return response
