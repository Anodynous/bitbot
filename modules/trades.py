import json

from modules.connect import bitfinexConnect


def trades(minsize=0, coin_pair='BTCUSD'):  # prints trades equal to or larger than 'minsize'
    ws = bitfinexConnect('trades', 'P0', coin_pair=coin_pair)
    while True:
        result = ws.recv()
        result = json.loads(result)
        try:
            if result[1] == 'te':
                if abs(float(result[5])) > float(minsize):
                    result_timestamp = datetime.now().strftime("%H:%M:%S.%f")
                    if float(result[5]) > 100:
                        print('\033[1;37;42mBUY:  {0} @ {1}\033[0m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) > 50:
                        print('\033[1;37;42mBUY:\033[1;32;0m\033[0;32;32m  {0} @ {1}\033[0m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) > 10:
                        print('\033[1;32;32mBUY:  {0} @ {1}\033[0m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) > 1:
                        print('\033[0;32;32mBUY:  {0} @ {1}\033[0m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) > 0:
                        print('\033[0;32;32mBUY:\033[0m  {0} @ {1} : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < -100:
                        print('\033[1;37;41mSELL: {0} @ {1}\033[0m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < -50:
                        print('\033[1;37;41mSELL:\033[1;31;0m\033[0;31;31m {0} @ {1}\033[0m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < -10:
                        print('\033[1;31;31mSELL: {0} @ {1}\033[0m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < -1:
                        print('\033[0;31;31mSELL: {0} @ {1}\033[0m : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
                    elif float(result[5]) < 0:
                        print('\033[0;31;31mSELL:\033[0m {0} @ {1} : {2}'.format(str(result[5]),str(result[4]), result_timestamp))
        except:
            print(json.dumps(result, indent = 4, sort_keys = True))
            continue
    ws.close()