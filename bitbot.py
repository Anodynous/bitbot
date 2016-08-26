#!/usr/bin/env python3
import sys

from modules.logger import trade_logger
from modules.orderbook import order_book
from modules.orderbook import raw_order_book
from modules.trades import trades
from modules.price import ticker


if sys.version_info[0] < 3:
        raise "Requires Python 3+"


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
