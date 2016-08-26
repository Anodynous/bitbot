import csv
import glob
import json
import sys
from datetime import datetime

from modules.connect import bitfinexConnect


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