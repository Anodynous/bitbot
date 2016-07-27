#!/usr/bin/env python3

import sys
import json
from websocket import create_connection

def trades(minsize):                                            #prints trades of at least minsize to prompt
    ws = create_connection("wss://api2.bitfinex.com:3000/ws")
    ws.send(json.dumps({
        "event": "subscribe",
        "channel": "trades",
        "pair" : "BTCUSD",
        "prec" : "P0"
       }))

    while True:
        result = ws.recv()
        result = json.loads(result)
        try:
            if result[1] == 'te':
                if abs(float(result[5])) > int(minsize):
                    if float(result[5]) > 0: print('BUY: '+ str(result[5]) +' @ '+ str(result[4]))
                    elif float(result[5]) < 0: print('SELL: '+ str(result[5]) +' @ '+ str(result[4]))
        except:
            continue
        #print(json.dumps(result, indent = 4, sort_keys = True))
    ws.close()
def ticker():                                            #prints ticker feed
    last_price = 0
    ws = create_connection("wss://api2.bitfinex.com:3000/ws")
    ws.send(json.dumps({
        "event": "subscribe",
        "channel": "ticker",
        "pair" : "BTCUSD",
        "prec" : "P0"
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





def main(argv):                                                 #main function
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
        else:
            print('check command line arguments')
    else:
        print('no command line arguments provided')

if __name__ == "__main__":                                      #calls main function
    main(sys.argv)
