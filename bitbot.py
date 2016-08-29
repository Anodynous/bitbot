#!/usr/bin/env python3
import sys
import argparse

from modules.logger import trade_logger
from modules.orderbook import order_book
from modules.orderbook import raw_order_book
from modules.trades import trades
from modules.price import ticker

if sys.version_info[0] < 3:
    sys.stdout.write('Sorry, requires Python 3+')
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Command line utility for Bitfinex API')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('minsize', metavar='size', type=float, help='minimum trade size or USD amount (orderbook)', nargs='?', default=0)
    parser.set_defaults(minsize=0)
    group.add_argument('-t', '--trades', help='live trade feed', action='store_true')
    group.add_argument('-ti', '--ticker', help='price ticker', action='store_true')
    group.add_argument('-l', '--log', help='log raw trade feed', action='store_true')
    group.add_argument('-o', '--orderbook', type=str, choices=['bid', 'ask', 'all'], default='bids', help='display orderbook', action='store')
    group.add_argument('-r', '--rawbook', help='show raw orderbook feed', action='store_true')
    args = parser.parse_args()
    if args.trades:
        trades(minsize=args.minsize)
    elif args.ticker:
        ticker()
    elif args.log:
        trade_logger()
    elif args.rawbook:
        raw_order_book()
    elif args.orderbook:
        order_book(ordertype=args.orderbook, price_range=args.minsize)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:   # cleaner exit without printing traceback on ctr+c
        pass