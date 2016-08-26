from websocket import create_connection, WebSocketTimeoutException
import json


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