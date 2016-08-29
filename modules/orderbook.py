import sys
import json
import requests
from datetime import datetime
from operator import itemgetter

from modules.connect import bitfinexConnect
from modules.price import current_price
from modules.output import output

def order_book(ordertype, price_range=0):  # outputs order book data
    ordertype = ordertype + 's'
    if price_range != 0:
        last_price = float(current_price())
    r = requests.get('https://api.bitfinex.com/v1/book/BTCUSD')
    parsed_json = json.loads(r.text)
    book_usd_value = 0
    book_btc_value = 0
    n = 0
    for i in range(0, 5000):
        try:
            usd_price = parsed_json[ordertype][i]['price']
            if (price_range == 0) or (last_price - float(price_range)) <= float(usd_price) <= (
                        last_price + float(price_range)):
                n += 1
                timestamp = datetime.fromtimestamp(int(float(parsed_json[ordertype][i]['timestamp'])))
                btc_amount = parsed_json[ordertype][i]['amount']
                usd_value = float(btc_amount) * float(usd_price)
                book_usd_value += usd_value
                book_btc_value += float(btc_amount)
                output(str(btc_amount) + ' BTC @ ' + str(usd_price) + ' USD. Placed: ' + str(
                    timestamp) + ' Valued: ' + str(usd_value) + ' USD')
        except:
            cumulative_usd = "{:,}".format(int(book_usd_value))
            cumulative_btc = "{:,}".format(int(book_btc_value))
            output('\n\n{0} {1} {2}'.format((n), ordertype[:-1], ' orders'))
            output('Cumulative value of: {0} {1}'.format(cumulative_usd, 'USD'))
            output('Cumulative quantity of: {0} {1}'.format(cumulative_btc, 'BTC'))
            sys.exit(1)


def raw_order_book():
    orderbook_length = 100
    precision = 'R0'
    ws = bitfinexConnect('book', precision, orderbook_length) #number of decimal places: P0=2, P1=1, P2=0 ie. $1, P3=-1 ie. $10
    while True:
        result = ws.recv()
        result = json.loads(result)
        if type(result) == list:
            if len(result) == 4 and result[1] != 'hb':
                for n in range(0, len(order_book)-1):
                    if result[1] == order_book[n][0]:
                        if result[3] != order_book[n][2]:
                            if result[2] != 0:
                                output(('UPDATE: , [{0}, {1}, {2}] :: {3}'.format(result[1], result[2], result[3], order_book[n])))
                                order_book[n] = [result[1], result[2], result[3]]
                                break
                            else:
                                del order_book[n]
                                output(('removed! book lenght now:', len(order_book)))
                        elif result[3] == order_book[n][2]:
                            break
                    elif n >= (len(order_book)-2) and result[2] != 0:
                        new_bookpoint = [result[1], result[2], result[3]]
                        order_book.append(new_bookpoint)
                        output(('APPEND: , [{0}, {1}, {2}]'.format(result[1], result[2], result[3])))
            elif len(result) == 2 and result[1] != 'hb':
                order_book = result[1]
                order_book = sorted(order_book, key = itemgetter(0), reverse = True)
    ws.close()