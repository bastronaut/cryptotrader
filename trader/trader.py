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
DROPVALUE = 0.90
GAINVALUE = 1.03
BACKUPGAINVALUE = 1.01 # value that, if crossed by this value over most recente salesprice, will be bought in for again
TRADINGFEE = 0.0025 # poloniex worst case fee

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

    lowestprice = anchorprice
    saleprice = anchorprice * DROPVALUE # init, at this price, sell if holding
    increase = saleprice * GAINVALUE # at this price, buy in again
    backupincrease = saleprice * BACKUPGAINVALUE # at this price, buy in again if price went up over sales price

    sidelined = False
    usd = 0
    ltcqty = 1
    feespaid = []
    print "starting LTC amount: {}, starting USD amount: {}".format(ltcqty, usd)
    print "anchorprice: {}, saleprice: {}, increase: {}, backupincrease: {}".format(anchorprice, saleprice, increase, backupincrease)

    for i in ltclist:
        curprice = i['weightedAverage']

        if curprice < lowestprice:
            lowestprice = curprice
            increase = lowestprice * GAINVALUE

        if curprice > anchorprice:
            anchorprice = curprice
            saleprice = anchorprice * DROPVALUE

        if sidelined:
            if curprice > backupincrease:
                '''Price over the top buy boundary, buy in again'''
                ltcqty = (usd / curprice) * (1-TRADINGFEE)
                fee = usd * TRADINGFEE
                feespaid.append(fee)
                print "bought {} at price {} for fee {} at backupprice".format(ltcqty, curprice, fee)
                usd = 0
                sidelined = False
                anchorprice = curprice
                saleprice = anchorprice * DROPVALUE
                increase = saleprice * GAINVALUE

            elif curprice > increase:
                '''Price over the bottom buy boundary, buy in again'''

                ltcqty = (usd / curprice) * (1-TRADINGFEE)
                fee = usd * TRADINGFEE
                feespaid.append(fee)
                print "bought {} at price {} for fee {} at increase price".format(ltcqty, curprice, fee)
                usd = 0
                sidelined = False
                anchorprice = curprice
                saleprice = anchorprice * DROPVALUE
                increase = saleprice * GAINVALUE





        if not sidelined:
            if curprice < saleprice:
                '''Price below sell threshold, sell'''
                usd = (ltcqty * curprice) * (1-TRADINGFEE)
                fee = (ltcqty * curprice) * TRADINGFEE
                feespaid.append(fee)
                print "sold {} at price {} for fee {}".format(ltcqty, curprice, fee)
                ltcqty = 0
                lowestprice = curprice
                sidelined = True
                backupincrease = curprice * BACKUPGAINVALUE


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
