import json

import requests

from modules.connect import bitfinexConnect
from modules.output import output

def ticker():  # outputs ticker feed
    last_price = 0
    ws = bitfinexConnect('ticker', 'P0')
    while True:
        result = ws.recv()
        result = json.loads(result)
        try:
            if result[2] != 'hb':
                if last_price != result[7]:
                    output(result[7])
                    last_price = result[7]
        except:
            continue
    ws.close()

def current_price():  # returns current BTC price
    r = requests.get('https://api.bitfinex.com/v1/pubticker/BTCUSD')
    parsed_json = json.loads(r.text)
    last_price = parsed_json['last_price']
    return last_price