import json
from datetime import datetime
from modules.connect import bitfinexConnect


def trades(minsize=0, coin_pair='BTCUSD'):  # prints trades equal to or larger than 'minsize'
    ws = bitfinexConnect('trades', 'P0', coin_pair=coin_pair)
    while True:
        result = ws.recv()
        result = json.loads(result)
        try:
            if result[1] == 'te':
                if abs(float(result[5])) > float(minsize):
                    trd_f = [32, 42]
                    if result[5] > 0:
                        trd_direction = 'BUY: '
                    else:
                        trd_direction = 'SELL:'
                        trd_f = [x - 1 for x in trd_f]
                    result_abs = abs(result[5])
                    result_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    result_format = (trd_direction, str(round(abs(result[5]), 5)).ljust(7), str(result[4]).rjust(10), result_timestamp.rjust(16))
                    if result_abs >= 100:
                        print('\033[1;37;'+ str(trd_f[1]) + 'm{0} {1} {2}\033[0m {3}'.format(*result_format))
                    elif result_abs >= 50:
                        print('\033[1;37;'+ str(trd_f[1]) + 'm{0}\033[1;'.format(trd_direction)+ str(trd_f[0]) + ';0m\033[0;'+ str(trd_f[0]) + ';'+ str(trd_f[0]) + 'm {1} {2}\033[0m {3}'.format(*result_format))
                    elif result_abs >= 10:
                        print('\033[1;'+ str(trd_f[0]) + ';'+ str(trd_f[0]) + 'm{0} {1} {2}\033[0m {3}'.format(*result_format))
                    elif result_abs >= 1:
                        print('\033[0;'+ str(trd_f[0]) + ';'+ str(trd_f[0]) + 'm{0} {1} {2}\033[0m {3}'.format(*result_format))
                    elif result_abs < 1:
                        print('\033[0;'+ str(trd_f[0]) + ';'+ str(trd_f[0]) + 'm{0}\033[0m {1} {2} {3}'.format(*result_format))
        except:
            if result['event'] == 'subscribed':
                print('Subscribed to {0} at {1}'.format(result['pair'], datetime.now().strftime('%H:%M:%S')))
            elif result['event'] != 'info':
                print(result)
            continue
    ws.close()