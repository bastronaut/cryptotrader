import importlib
key = importlib.import_module('apikey')
polo = importlib.import_module('api')
database = importlib.import_module('database')
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("k", help="api key")
parser.add_argument("s", help="api secret")
import time
import datetime

CURRENCYPAIR = "USDT_LTC"
ONEWEEKSECONDS = 604800
NROFWEEKS = 8
DROPVALUE = 0.93
GAINVALUE = 1.04
BACKUPGAINVALUE = 1.025 # value that, if crossed by this value over most recente salesprice, will be bought in for again
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

    curprice = ltclist[0]['weightedAverage']

    lowestprice = curprice
    topprice = curprice
    sellprice = curprice * DROPVALUE # init, at this price, sell if holding
    buybottom = sellprice * GAINVALUE # at this price, buy in again
    buytop = sellprice * BACKUPGAINVALUE # at this price, buy in again - price in case buy bottom is never touched
    sidelined = False
    usd = 0
    ltcqty = 1
    feespaid = []
    print "starting LTC amount: {}, starting USD amount: {}".format(ltcqty, usd)
    print "curprice: {}, sellprice: {}, buybottom: {}, buytop: {}".format(curprice, sellprice, buybottom, buytop)

    for i in ltclist:
        curprice = i['weightedAverage']

        if curprice < lowestprice:
            lowestprice = curprice
            buybottom = lowestprice * GAINVALUE

        if curprice > topprice:
            topprice = curprice
            sellprice = topprice * DROPVALUE

        if sidelined:
            if curprice > buytop:
                # do buy
                ltcqty = (usd / curprice) * (1-TRADINGFEE)
                fee = usd * TRADINGFEE
                usd = 0
                feespaid.append(fee)
                dateepoch = i['date']
                date = datetime.datetime.fromtimestamp(dateepoch).strftime('%Y-%m-%d %H:%M:%S')
                print "bought {} at price {} for fee {} at backupprice, on date {}\n".format(ltcqty, curprice, fee, date)

                sidelined = False
                topprice = curprice
                sellprice = topprice * DROPVALUE

            elif curprice > buybottom:
                # do buy
                ltcqty = (usd / curprice) * (1-TRADINGFEE)
                fee = usd * TRADINGFEE
                usd = 0
                feespaid.append(fee)
                dateepoch = i['date']
                date = datetime.datetime.fromtimestamp(dateepoch).strftime('%Y-%m-%d %H:%M:%S')
                print "bought {} at price {} for fee {} at backupprice, on date {}\n".format(ltcqty, curprice, fee, date)

                sidelined = False
                topprice = curprice
                sellprice = topprice * DROPVALUE

        if not sidelined:
            if curprice < sellprice:
                # do sell
                usd = (ltcqty * curprice) * (1-TRADINGFEE)
                fee = (ltcqty * curprice) * TRADINGFEE
                feespaid.append(fee)
                dateepoch = i['date']
                date = datetime.datetime.fromtimestamp(dateepoch).strftime('%Y-%m-%d %H:%M:%S')
                print "sold {} at price {} for fee {} on date {}\n".format(ltcqty, curprice, fee, date)

                ltcqty = 0

                sidelined = True
                buytop = curprice * BACKUPGAINVALUE
                buybottom = curprice * GAINVALUE
                lowestprice = curprice





        #
        # if curprice < lowestprice:
        #     lowestprice = curprice
        #     buybottom =
        #
        # if curprice > anchorprice:
        #     anchorprice = curprice
        #     saleprice = anchorprice * DROPVALUE
        #
        # if sidelined:
        #     if curprice > backupincrease:
        #         '''Price over the top buy boundary, buy in again'''
        #         ltcqty = (usd / curprice) * (1-TRADINGFEE)
        #         fee = usd * TRADINGFEE
        #         feespaid.append(fee)
        #         print "bought {} at price {} for fee {} at backupprice".format(ltcqty, curprice, fee)
        #         usd = 0
        #         sidelined = False
        #         anchorprice = curprice
        #         saleprice = anchorprice * DROPVALUE
        #         increase = saleprice * GAINVALUE
        #
        #     elif curprice > increase:
        #         '''Price over the bottom buy boundary, buy in again'''
        #
        #         ltcqty = (usd / curprice) * (1-TRADINGFEE)
        #         fee = usd * TRADINGFEE
        #         feespaid.append(fee)
        #         print "bought {} at price {} for fee {} at increase price".format(ltcqty, curprice, fee)
        #         usd = 0
        #         sidelined = False
        #         anchorprice = curprice
        #         saleprice = anchorprice * DROPVALUE
        #         increase = saleprice * GAINVALUE
        #
        #
        #
        #
        #
        # if not sidelined:
        #     if curprice < saleprice:
        #         '''Price below sell threshold, sell'''
        #         usd = (ltcqty * curprice) * (1-TRADINGFEE)
        #         fee = (ltcqty * curprice) * TRADINGFEE
        #         feespaid.append(fee)
        #         print "sold {} at price {} for fee {}".format(ltcqty, curprice, fee)
        #         ltcqty = 0
        #         lowestprice = curprice
        #         sidelined = True
        #         backupincrease = curprice * BACKUPGAINVALUE



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
