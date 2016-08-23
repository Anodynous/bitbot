#!/usr/bin/env python3

import sys
import json
import glob
import requests
import csv
from datetime import datetime
from websocket import create_connection, WebSocketTimeoutException
from operator import itemgetter

if sys.version_info[0] < 3:
        raise "Requires Python 3+"

def bitfinexConnect(channel, precision, orderbook=25, coin_pair='BTCUSD'):
    ws = create_connection("wss://api2.bitfinex.com:3000/ws", timeout=5)
    if orderbook == 0:
        ws.send(json.dumps({
            "event": "subscribe",
            "channel": channel,
            "pair": coin_pair,
            "prec": precision
        }))
    elif orderbook != 0:
        ws.send(json.dumps({
            "event": "subscribe",
            "channel": channel,
            "pair": coin_pair,
            "prec": precision,
            "len": orderbook
        }))
    return(ws)


def trades(minsize=0, coin_pair='BTCUSD'):  # prints trades equal to or larger than 'minsize'
    ws = bitfinexConnect('trades', 'P0', coin_pair=coin_pair)
    while True:
        result = ws.recv()
        result = json.loads(result)
        try:
            if result[1] == 'te':
                if abs(float(result[5])) > float(minsize):
                    result_timestamp = datetime.now().strftime("%H:%M:%S.%f")
                    if float(result[5]) > 30:
                        print('\033[1;37;42mBUY:  {0} @ {1}\033[0;37;40m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) > 10:
                        print('\033[1;37;42mBUY:\033[1;32;40m  {0} @ {1} : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) > 5:
                        print('\033[1;32;40mBUY:  {0} @ {1} : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) > 0:
                        print('\033[0;32;40mBUY:  {0} @ {1} : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < -30:
                        print('\033[1;37;41mSELL: {0} @ {1}\033[0;37;40m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < -10:
                        print('\033[1;37;41mSELL:\033[1;31;40m {0} @ {1} : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < -5:
                        print('\033[1;31;40mSELL: {0} @ {1} : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < 0:
                        print('\033[0;31;40mSELL: {0} @ {1} : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
        except:
            print(json.dumps(result, indent = 4, sort_keys = True))
            continue
    ws.close()


def ticker():  # prints ticker feed
    last_price = 0
    ws = bitfinexConnect('ticker', 'P0')
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
    ws.close()

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
                                print('UPDATE: , [{0}, {1}, {2}] :: {3}'.format(result[1], result[2], result[3], order_book[n]))
                                order_book[n] = [result[1], result[2], result[3]]
                                break
                            else:
                                del order_book[n]
                                print('removed! book lenght now:', len(order_book))
                        elif result[3] == order_book[n][2]:
                            break
                    elif n >= (len(order_book)-2) and result[2] != 0:
                        new_bookpoint = [result[1], result[2], result[3]]
                        order_book.append(new_bookpoint)
                        print('APPEND: , [{0}, {1}, {2}]'.format(result[1], result[2], result[3]))
            elif len(result) == 2 and result[1] != 'hb':
                order_book = result[1]
                order_book = sorted(order_book, key = itemgetter(0), reverse = True)
    ws.close()

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
    ws = bitfinexConnect('trades', 'R0')
    log = open(last_logfile, 'a')
    writer = csv.writer(log, dialect='excel')
    timestamp = datetime.now()
    writer.writerow(['','','','','','','','Logstart',timestamp])
    print('Started logging at {0} to file {1} after row {2}'.format(timestamp, last_logfile, trade_count))
    while True:
        try:
            result = ws.recv()
            result = json.loads(result)
            #if (type(result) == list) and (result[1] == 'hb'):
            if (type(result) == list) and (result[1] == 'tu'):
                try:
                    if result[1] == 'tu':
                        if trade_count >= 100000: # splits CSV files after 100.000 trades
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
        except WebSocketTimeoutException as e:
            print(e)
            trade_logger()
    ws.close()

def main():  # main function
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h':
            print('options:\n-trades (coin_pair minsize)\n-ticker\n-log\n-raw\n-orderbook (asks/bids range)')
        elif sys.argv[1] == '-trades':
            if len(sys.argv) > 2:
                try:
                    trades(sys.argv[3], sys.argv[2])
                except:
                    trades(coin_pair=sys.argv[2])
            elif len(sys.argv) > 1:
                try:
                    trades(sys.argv[2])
                except:
                    trades()
        elif sys.argv[1] == '-ticker':
            ticker()
        elif sys.argv[1] == '-log':
            trade_logger()
        elif sys.argv[1] == '-raw':
            raw_order_book()
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
