from menu.app import app
import os, json
from menu.fetcher import Fetcher

def resetCache():
    currentDir = os.path.dirname(os.path.realpath(__file__))
    configPath = os.path.join(currentDir, '../config.json')
    with open(configPath, 'r') as f:
        config = json.load(f)
    config['cache'] = config['cache'].replace('$HERE', os.path.join(currentDir, '..'))
    fetch = Fetcher(config)
    fetch.resetCache()