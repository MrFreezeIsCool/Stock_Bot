from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd
import json
import time

BASE_URL = "https://paper-api.alpaca.markets"
KEY_ID = "PKKR6QBBLW6PJSXNA3NU"
SECRET_KEY = "ytMJYuJnNlzPi2vTNWgENEVqsr74SjGCErvXSmgN"
api = REST(key_id=KEY_ID,secret_key=SECRET_KEY,base_url="https://paper-api.alpaca.markets")
active_assets = api.list_assets(status='active')
stocks = [a for a in active_assets if a.easy_to_borrow == True if a.shortable == True if a.exchange == 'NASDAQ']
clock = api.get_clock()
if clock.is_open == False:
    exit()



def jsonParser(Ticker):
    # Converts the data into a json compatable format
    bars = api.get_bars(Ticker, TimeFrame.Hour).df
    result = bars.to_json(orient="index")
    parsed = json.loads(result)
    return parsed


def readFile(path, ticker):
    # Opens the choosen file and returns the section requested
    file = open(path)
    read = json.loads(file.read())
    return read[ticker]


def toTheBottom(dic):
    # Method returns a nested dictionary
    for key, value in dic.items():
        if type(value) is dict:
            toTheBottom(value)
        else:
            return dic


def writeFile(data, fileName):
    # Writes the given data to a json file
    with open("data.json", "w") as fileName:
        json.dump(data, fileName, indent=4)




data = {

}

count = 0
for asset in stocks:
    data[f"{asset.symbol}"] = jsonParser(f"{asset.symbol}")

def AdjCreater(data, file):
    for stock in reversed(data):
        indStockData = (readFile(file,stock))
        count  = 0
        for dates in indStockData:
            DataPoint = toTheBottom(indStockData[dates])
            if(count != 0):
                DataPoint['adjopen'] = (OldOpen+OldClose)/2
                DataPoint['adjlow'] = (DataPoint['low'])
                DataPoint['adjhigh'] = (DataPoint['high'])
                DataPoint['adjclose'] = (DataPoint['low'] + DataPoint['high'] + DataPoint['open'] + DataPoint['close'])/4
            OldOpen = DataPoint['open']
            OldClose = DataPoint['close']
            count += 1
        data[stock] = indStockData
    return data


def MakeMoney(indStockData, stock):
    count = 0
    for dates in reversed(indStockData):
        DataPoint = toTheBottom(indStockData[dates])
        if(count <5 and len(indStockData) > 4):
            print(stock)
            if(count == 0):
                OldestDataOpen = DataPoint['adjopen']
            if(count == 1):
                OldDataOpen = DataPoint['adjopen']
            if(count == 2):
                NewDataOpen = DataPoint['adjopen']
            if(count == 3):
                NewestDataOpen = DataPoint['adjopen']
                NewestDataClose = DataPoint['adjclose']
            if(count == 4):
                if(OldestDataOpen>OldDataOpen and OldDataOpen> NewDataOpen and NewDataOpen < NewestDataOpen):
                    q = (20000/NewestDataClose)
                    q = int(q)
                    print('Buying ' + str(q) + " " + stock)
                    try:
                        api.submit_order(symbol=stock, qty=q, side='buy', type='market', time_in_force='gtc' )
                    except:
                        print("Couldn't buy " + stock)
                if(OldestDataOpen < OldDataOpen and OldDataOpen < NewDataOpen and NewDataOpen > NewestDataOpen):
                    q = 0
                    try:
                        position = api.get_position(stock)
                        q = position.qty
                        q = int(q)
                    except:
                        print("No position")
                    if q <= 0:
                        q = (20000/NewestDataClose)
                        q = int(q)
                    print('Selling ' + str(q) + " " + stock)
                    try:
                        api.submit_order(symbol=stock, qty=q, side='sell', type='market', time_in_force='gtc' )
                    except:
                        print("Couldn't sell " + stock)
        count += 1




writeFile(data, "data.json")
writeFile(AdjCreater(data, "data.json"), 'data.json')
for stock in data:
    name = str(stock)
    MakeMoney(readFile('data.json', stock), name)



           
       
   


#In case we need to convert to a normal time  
# for times in parsed:
#     times = int(times)/1000
#     times = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(times)