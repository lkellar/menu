from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

from menu.fetcher import Fetcher
from menu.util import genDate, getMonday
from menu.gen import genHTML

app = Flask(__name__, static_url_path='/static', static_folder='../static/')
fetch = None


@app.before_first_request
def startup():
    global fetch
    currentDir = os.path.dirname(os.path.realpath(__file__))
    configPath = os.path.join(currentDir, '../config.json')
    with open(configPath, 'r') as f:
        config = json.load(f)
    config['cache'] = config['cache'].replace('$HERE', os.path.join(currentDir, '..'))
    fetch = Fetcher(config)

@app.route('/')
def index():
    date = datetime.today()
    data = fetch.week(getMonday(date))
    return genHTML(data, request.url_root, date)

@app.route('/info')
def info():
    return app.send_static_file('index.html')


@app.route('/week')
def week():
    return jsonify(fetch.week(getMonday()))


@app.route('/api')
def api():
    wordify = False
    modifier = 0
    if request.args.get('wordify') == 'true':
        wordify = True
    if request.args.get('days'):
        modifier = int(request.args.get('days'))
    date = genDate(modifier)
    return jsonify(fetch.get(wordify, date))


if __name__ == '__main__':
    app.run()
