import importlib
key = importlib.import_module('apikey')
polo = importlib.import_module('api')
database = importlib.import_module('database')
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("k", help="api key")
parser.add_argument("s", help="api secret")
import time

CURRENCYPAIR = "USDT_LTC"
ONEWEEKSECONDS = 604800
NROFWEEKS = 8
DROPVALUE = 0.88
GAINVALUE = 1.07

def main():
    args = parser.parse_args()
    apikey = key.apikey(args.k, args.s)
    api = polo.poloniex(apikey.getkey, apikey.getsecret)
    db = database.database('chartdata')
    #collect_chart_data(api, db)
    backtest(db)


def backtest(db):
    ltccol = db.getdb()['usdt_ltc']
    ltcdatesorted = ltccol.find().sort("date", 1)
    ltclist = []
    for i in ltcdatesorted:
        ltclist.append(i)
    print len(ltclist)

    anchorprice = ltclist[0]['weightedAverage']
    drop = anchorprice * DROPVALUE
    increase = drop * GAINVALUE
    sidelined = False
    usd = 0
    ltcqty = 1
    print "starting LTC amount: {}".format(ltcqty)
    print "starting USD amount: {}".format(usd)
    print "anchorprice: {}, drop: {}, increase: {}".format(anchorprice, drop, increase)
    for i in ltclist:
        curprice = i['weightedAverage']
        if curprice > anchorprice:
            anchorprice = curprice
            drop = anchorprice * DROPVALUE
            increase = drop * GAINVALUE
            # print "setting anchorprice: {} setting drop: {} setting increase {}".format(anchorprice, drop, increase)

        if sidelined:
            if curprice > increase:
                ltcqty = usd / curprice
                print "bought " + str(ltcqty) + " at price " + str(curprice)
                usd = 0
                sidelined = False
                anchorprice = curprice
                drop = anchorprice * DROPVALUE
                increase = drop * GAINVALUE




        if not sidelined:
            if curprice < drop:
                usd = ltcqty * curprice
                print "sold " + str(ltcqty) + " at price " + str(curprice)
                ltcqty = 0
                sidelined = True


    print "Resulting ltc: " + str(ltcqty)
    print "Result usd: " + str(usd)





def collect_chart_data(api, db):
    for i in range(NROFWEEKS):
        result = getdata(api, i)
        print "nr of results: " + str(len(result))
        db.save("usdt_ltc", result)
        time.sleep(0.5) # avoid spamming API

def getdata(api, i):
    period = 900 # 15 min interval
    timestampNow = int(time.time())
    end = timestampNow - (i * ONEWEEKSECONDS)
    start = timestampNow - ((i+1) * ONEWEEKSECONDS)
    print "getting for start: " + str(start) + " and end: " + str(end)
    return api.returnChartData(CURRENCYPAIR, period, start, end)



if __name__ == "__main__":
    main()
