from flask import Flask, request, jsonify
from os import path
import json
import sqlite3

from menu.fetcher import Fetcher
from menu.util import genDate, getMonday
from menu.gen import genHTML

app = Flask(__name__, static_url_path='/static', static_folder='../static/')
fetch = None

errormsg = 'The requested menu data is not available now'

@app.before_first_request
def startup():
    global fetch
    global config
    currentDir = path.dirname(path.realpath(__file__))
    configPath = path.join(currentDir, '../config.json')
    with open(configPath, 'r') as f:
        config = json.load(f)
    config['cache'] = config['cache'].replace('$HERE', path.join(currentDir, '..'))
    fetch = Fetcher(config)

@app.route('/')
def index():
    modifier = 0
    weeks = request.args.get('weeks')
    if weeks:
        modifier = int(weeks) * 7
    entry = request.args.get('entry')
    if not entry:
        entry = None
    date = genDate(modifier)
    with sqlite3.connect(config['cache']) as conn:
        c = conn.cursor()
        data = fetch.week(c, getMonday(date))
        c.close()

    valid = {key: value for key, value in data.items() if value != errormsg}
    if len(valid) == 0:
        return app.send_static_file('error.html')
    else:
        return genHTML(valid, request.url_root, date, entry)

@app.route('/week')
def week():
    modifier = 0
    weeks = request.args.get('weeks')
    if weeks:
        modifier = int(weeks) * 7
    date = genDate(modifier)
    with sqlite3.connect(config['cache']) as conn:
        c = conn.cursor()
        data = jsonify(fetch.week(c, getMonday(date)))
        c.close()
    return data


@app.route('/api')
def api():
    wordify = False
    modifier = 0
    if request.args.get('wordify') == 'true':
        wordify = True
    if request.args.get('days'):
        modifier = int(request.args.get('days'))
    date = genDate(modifier)

    with sqlite3.connect(config['cache']) as conn:
        c = conn.cursor()
        data = jsonify(fetch.prepAndGet(c, wordify, date))
        c.close()

    return data


if __name__ == '__main__':
    app.run()
