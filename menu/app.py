from datetime import date
import json
from os import path
from flask import Flask, jsonify
from flask.json import JSONEncoder
from menu.models import db
from menu.fetch import Fetcher

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

app = Flask(__name__)
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


@app.route('/fetch')
def fetch_test():
    # A simple /fetch api endpoint used for testing
    # will eventually be fleshed out with params and such
    return jsonify(fetchster.fetch_days(5))


if __name__ == "__main__":
    app.run()
