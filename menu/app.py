from datetime import date, datetime
import json
from os import path
from flask import Flask, jsonify, render_template, request
from flask.json import JSONEncoder
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from menu.models import db
from menu.fetch import Fetcher
from menu.scrapers.sage import SageConfig, SageScraper, DOT_TO_COLORS, STATION_TITLES

current_dir = path.dirname(path.realpath(__file__))

with open(path.join(current_dir, '../', 'config.json'), 'r') as f:
    config = json.load(f)

    # Replace $HERE in a db_path with the path of the config file
    config['db_path'] = config['db_path'].replace('$HERE', path.join(current_dir, '..'))

# If a sentry URL exists, enable sentry error reporting
if 'sentry_dsn' in config:
    sentry_sdk.init(
        dsn=config['sentry_dsn'],
        integrations=[FlaskIntegration(), SqlalchemyIntegration()]
    )

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
    fetchster = Fetcher(db, config['timezone'], config['sage']['menu_titles'])

@app.route('/')
def index():
    # The main webview for the menu
    if request.args.get('offset'):
        offset = int(request.args.get('offset'))
    else:
        offset = 0

    menu_data = fetchster.fetch_days(5, offset=offset)

    if not menu_data:
        return render_template('notfound.html', offset=offset)

    return render_template('index.html', menu_data=menu_data, datetime=datetime,
                           titles=config['sage']['menu_titles'], DOT_TO_COLORS=DOT_TO_COLORS,
                           STATION_TITLES=STATION_TITLES, config=config, offset=offset)


@app.route('/fetch')
def fetch():
    # A simple fetch api to hit the DB
    # Accepts a days param for the amount of days
    # and a date param for the start date in YYYY-MM-DD format
    # both parameters are optional
    if request.args.get('days'):
        days = int(request.args.get('days'))
        if days == 0:
            return jsonify([])
    else:
        days = 1

    if request.args.get('offset'):
        offset = int(request.args.get('offset'))
    else:
        offset = 0

    start_date = None

    if request.args.get('date'):
        try:
            start_date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
        except ValueError:
            pass

    return jsonify(fetchster.fetch_days(days, start=start_date, offset=offset))

@app.route('/wordify')
def wordify():
    # An endpoint for a human readable description of the menu
    return jsonify(fetchster.wordify())

@app.route('/scrape', methods=['POST'])
def scrape():
    # A function to scrape the Sage if authentication is provided
    # First check and see if the scrape_key actually exists
    if 'scrape_key' in config:
        # If so, check if the user provided scrape key matches our scrape key
        if request.form.get('scrape_key') == config['scrape_key']:
            # If so, do some exciting scrpaing
            sage_config = SageConfig(config['sage']['email'], config['sage']['password'],
                                     config['sage']['unit_id'], config['sage']['menu_id'])

            sage_scraper = SageScraper(sage_config, db)
            sage_scraper.scrape()
            # Then return nothing, yes
            return '', 204

        # If not, tell the user that they did it wrong
        return 'Incorrect/Missing Scrape Key', 401

    # If not, tell the user that we did it wrong
    return 'No Scrape Key in config.json 🤷', 501

if __name__ == "__main__":
    app.run()
