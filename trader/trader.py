import importlib
key = importlib.import_module('apikey')
polo = importlib.import_module('api')
import argparse
1512596339827


parser = argparse.ArgumentParser()
parser.add_argument("k", help="api key")
parser.add_argument("s", help="api secret")
import time

CURRENCYPAIR = "USDT_BTC"
START = "1512595000"
END = "1512596421"

def main():
    args = parser.parse_args()
    apikey = key.apikey(args.k, args.s)
    api = polo.poloniex(apikey.getkey, apikey.getsecret)
    timestamp = int(time.time())
    print timestamp
    # https://poloniex.com/public?command=returnTradeHistory&currencyPair=USDT_BTC&start=1512590000&end=1512596421
    options = {"currencyPair": CURRENCYPAIR, "startDate": START, "endDate": END}
    print api.returnMarketTradeHistory(options)

if __name__ == "__main__":
    main()
