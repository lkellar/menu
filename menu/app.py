from datetime import date, datetime
import json
from os import path
from flask import Flask, jsonify, render_template, request
from flask.json import JSONEncoder
from menu.models import db
from menu.fetch import Fetcher
from menu.scrapers.sage import SageConfig, SageScraper, DOT_TO_COLORS, STATION_TITLES

current_dir = path.dirname(path.realpath(__file__))

with open(path.join(current_dir, '../', 'config.json'), 'r') as f:
    config = json.load(f)

    # Replace $HERE in a db_path with the path of the config file
    config['db_path'] = config['db_path'].replace('$HERE', path.join(current_dir, '..'))

# Custom JSON Encoder for flask to format all dates in YYYY-MM-DD format
class CustomJSONEncoder(JSONEncoder):
    #pylint: disable=method-hidden, arguments-differ
    def default(self, obj):
        try:
            if isinstance(obj, date):
                # If a date, format it to YYYY-MM-DD
                return obj.strftime('%Y-%m-%d')
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app = Flask(__name__, static_folder='../static', static_url_path='/static',
            template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config["db_path"]}'
# Turn off the track modifications setting for the db, as it's not used,
# and by turning it off, we gain performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Use the custom json encoder defined above
app.json_encoder = CustomJSONEncoder

@app.before_first_request
def startup():
    # It's alright to not have the global variable defined in module level because the startup
    # function should ALWAYS run before any other function that needs it
    #pylint: disable=global-variable-undefined
    global fetchster

    db.init_app(app)
    db.create_all()

    # create a global fetcher for use by all functions
    fetchster = Fetcher(db, config['timezone'])

@app.route('/')
def index():
    # The main webview for the menu
    menu_data = fetchster.fetch_days(5)
    return render_template('index.html', menu_data=menu_data, datetime=datetime,
                           titles=config['sage']['menu_titles'], DOT_TO_COLORS=DOT_TO_COLORS,
                           STATION_TITLES=STATION_TITLES)


@app.route('/fetch')
def fetch_test():
    # A simple /fetch api endpoint used for testing
    # will eventually be fleshed out with params and such
    if request.args.get('days'):
        days = int(request.args.get('days'))
    else:
        days = 5

    return jsonify(fetchster.fetch_days(days))

@app.route('/scrape')
def scrape_test():
    # A simple test for scrape or whatever
    sage_config = SageConfig(config['sage']['email'], config['sage']['password'],
                             config['sage']['unit_id'], config['sage']['menu_id'])

    sage_scraper = SageScraper(sage_config, db)
    sage_scraper.scrape()
    return '200'


if __name__ == "__main__":
    app.run()
