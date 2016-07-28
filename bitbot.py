#!/usr/bin/env python3

import sys
import json
import glob
import requests
import csv
from datetime import datetime
from websocket import create_connection

if sys.version_info[0] < 3:
        raise "Requires Python 3+"

def trades(minsize):  # prints trades equal to or larger than 'minsize'
    ws = create_connection("wss://api2.bitfinex.com:3000/ws")
    ws.send(json.dumps({
        "event": "subscribe",
        "channel": "trades",
        "pair": "BTCUSD",
        "prec": "P0"
    }))

    while True:
        result = ws.recv()
        result = json.loads(result)
        try:
            if result[1] == 'te':
                if abs(float(result[5])) > int(minsize):
                    if float(result[5]) > 0:
                        print('BUY: ' + str(result[5]) + ' @ ' + str(result[4]))
                    elif float(result[5]) < 0:
                        print('SELL: ' + str(result[5]) + ' @ ' + str(result[4]))
        except:
            continue
            # print(json.dumps(result, indent = 4, sort_keys = True))
    ws.close()


def ticker():  # prints ticker feed
    last_price = 0
    ws = create_connection("wss://api2.bitfinex.com:3000/ws")
    ws.send(json.dumps({
        "event": "subscribe",
        "channel": "ticker",
        "pair": "BTCUSD",
        "prec": "P0"
    }))

    while True:
        result = ws.recv()
        result = json.loads(result)
        try:
            if result[2] != 'hb':
                if last_price != result[7]:
                    print(result[7])
                    last_price = result[7]
        except:
            continue


def current_price():  # returns current BTC price
    r = requests.get('https://api.bitfinex.com/v1/pubticker/BTCUSD')
    parsed_json = json.loads(r.text)
    last_price = parsed_json['last_price']
    return last_price


def order_book(ordertype, price_range=0):  # prints order book data
    if price_range != 0:
        last_price = float(current_price())
    r = requests.get('https://api.bitfinex.com/v1/book/BTCUSD')
    parsed_json = json.loads(r.text)
    book_usd_value = 0
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
                print(str(btc_amount) + ' BTC @ ' + str(usd_price) + ' USD. Placed: ' + str(
                    timestamp) + ' Valued: ' + str(usd_value) + ' USD')
        except:
            print('\n\n', (n + 1), ' ', ordertype, ' orders')
            print('Combined value of: {:,}'.format(int(book_usd_value)), ' USD')
            sys.exit(1)


def trade_logger_filechk():  # picks logfile to continue from and gets linecount
    logfile = glob.glob('bitfinex_tradelog*')
    if len(logfile) < 1:
        open('bitfinex_tradelog1.csv', 'a').close()  # creates first logfile if none are present
        last_logfile = 'bitfinex_tradelog1.csv'
    else:
        try:
            try:
                last_logfile = max(glob.glob('bitfinex_tradelog???.csv'))
            except ValueError:
                last_logfile = max(glob.glob('bitfinex_tradelog??.csv'))
        except ValueError:
            last_logfile = max(glob.glob('bitfinex_tradelog?.csv'))
    with open(last_logfile) as f:
        for i, l in enumerate(f):
            pass
    try:
        i += 1
    except NameError:
        i = 0
    return last_logfile, i


def trade_logger():  # logs all trades in CSV format
    last_logfile, trade_count = trade_logger_filechk()
    print(last_logfile, trade_count)
    ws = create_connection("wss://api2.bitfinex.com:3000/ws")
    ws.send(json.dumps({
        "event": "subscribe",
        "channel": "trades",
        "pair": "BTCUSD",
        "prec": "P0"
    }))
    while True:
        result = ws.recv()
        result = json.loads(result)
        #if (type(result) == list) and (result[1] == 'hb'):
        if (type(result) == list) and (result[1] == 'tu'):
            try:
                if result[1] == 'tu':
                    if trade_count >= 5000:
                        last_logfile = 'bitfinex_tradelog' + str(int(last_logfile[17:][:-4]) + 1) + '.csv'
                        trade_count = 0
                    trade_count += 1
                    log = open(last_logfile, 'a')
                    writer = csv.writer(log, dialect='excel')
                    writer.writerow(result)
                    print('.', end='')
                    sys.stdout.flush()
            except Exception as e:
                log = open(last_logfile, 'a')
                writer = csv.writer(log, dialect='excel')
                writer.writerow(e)
                print(e)
                pass

def main():  # main function
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h':
            print('HELP...')
        elif sys.argv[1] == '-trades':
            try:
                trades(sys.argv[2])
            except:
                trades(0)
        elif sys.argv[1] == '-ticker':
            ticker()
        elif sys.argv[1] == '-log':
            trade_logger()
        elif sys.argv[1] == '-orderbook':
            if len(sys.argv) > 2:
                if sys.argv[2] in ('asks', 'bids'):
                    if len(sys.argv) > 3:
                        if 0 <= int(sys.argv[3]) <= 1000:
                            order_book(sys.argv[2], sys.argv[3])
                        else:
                            print('check range attribute')
                    else:
                        order_book(sys.argv[2])
                else:
                    print("please define either 'asks' or 'bids'")
            else:
                print("please define either 'asks' or 'bids'")
        else:
            print('check command line arguments')
    else:
        print('no command line arguments provided')


if __name__ == "__main__":  # calls main function
    main()
