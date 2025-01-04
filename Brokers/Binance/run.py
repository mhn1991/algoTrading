from Brokers.Binance.instrument import Instrument as BinanceInstrument
from Analysis.Indicators.indicators import BollingerBands,StochasticRSI
from time import sleep
import datetime

from objects.Trade import Trade

lowerTimeFrameList = {"15m": "5m", "5m":"1m", "1m": "1s", "1s": ""}

def findSignal(closePrice,highPrice,lowPrice, upper_band, lower_band, stochRSIK, rsi, file) -> str:
    file.write("candle price: " + str(closePrice)+" RSI: " + str(rsi) + " stochRSI: " + str(stochRSIK)+" upper bond: " + str(upper_band)+" lower bond: " + str(lower_band))
    print("candle price: " + str(closePrice)+" RSI: " + str(rsi) + " stochRSI: " + str(stochRSIK)+" upper bond: " + str(upper_band)+" lower bond: " + str(lower_band))
    # base case for set up a sell trade
    if closePrice >= upper_band and stochRSIK == 100.0 and rsi > 75.0:
        return "SELL"
    #base case for set up a buy trade
    if closePrice <= lower_band and stochRSIK == 0.0 and rsi < 25.0:
        return "BUY"

    # here we satisfied partially so we are going to a smaller time frame
    if (highPrice >= upper_band or stochRSIK > 85) or (lowPrice <= lower_band or stochRSIK < 15):
        return "PARTIAL"

    return ""


def isSignal(signal: str, marketPrice,coinName, timeframe, file, tradeList, startTime=None, endTime=None, recurseAllowed=False):
    startTimeFormated = datetime.datetime.fromtimestamp(startTime/1000).strftime('%Y-%m-%d %H:%M:%S')
    endTimeFormated = datetime.datetime.fromtimestamp(endTime/1000).strftime('%Y-%m-%d %H:%M:%S')
    file.write("we are checking for signal from time: " + startTimeFormated + "till time: "+endTimeFormated+"\n")
    print("we are checking for signal from time: " + startTimeFormated + "till time: "+endTimeFormated)
    if signal == "SELL":
        trade = Trade("SELL", marketPrice, startTime, False)
        closeTrades("Buy", tradeList, marketPrice)
        tradeList.append(trade)
        file.write("##########################################\nSELL\n")
        file.write("we are in timeframe: " + timeframe + "\n")
        file.write("we are checking for signal from time: " + startTimeFormated + "till time: " + endTimeFormated + "\n")
        print("##########################################\nSELL")
        print("we are checking for signal from time: " + startTimeFormated + "till time: " + endTimeFormated)
    elif signal == "BUY":
        file.write("##########################################\nBUY\n")
        file.write("we are in timeframe: " + timeframe + "\n")
        file.write("we are checking for signal from time: " + startTimeFormated + "till time: " + endTimeFormated + "\n")
        print("##########################################\nBUY")
        print("we are checking for signal from time: " + startTimeFormated + "till time: " + endTimeFormated)
        trade = Trade("BUY", marketPrice, startTime, False)
        closeTrades("Sell", tradeList, marketPrice)
        tradeList.append(trade)
    elif signal == "PARTIAL":
        file.write("##########################################\nPARTIAL\n")
        file.write("we are in timeframe: " + timeframe + "\n")
        file.write("we are checking for signal from time: " + startTimeFormated + "till time: " + endTimeFormated + "\n")
        print("##########################################\nPARTIAL")
        print("we are checking for signal from time: " + startTimeFormated + "till time: " + endTimeFormated)
        if recurseAllowed:
            run(coinName, timeframe, file, tradeList, startTime, endTime)


def closeTrades(signal, tradeList, price):
    if len(tradeList) > 0:
        for currentTrade in tradeList:
            if not currentTrade.isComplete and currentTrade.tradeSide == signal:
                currentTrade.isComplete = True
                currentTrade.priceExit = price
                currentTrade.setProfit()


# I need better logic than sleep probably checking if the time is more than the close time of the last candle then execute
def run(coinName, timeframe, file, tradeList, startTime=None, endTime=None):
    instrument = BinanceInstrument(coinName, timeframe)
    df = instrument.getChart()
    df = BollingerBands(df)
    df = StochasticRSI(df)
    newKlineAdded = False
    file.write("===============================================\n")
    file.write("we are in timeframe: " + timeframe + "\n"+"previous candle time: "+str(df.iloc[-2]['OpenTime'])+"\n"+"current candle time: "+str(df.iloc[-1]['OpenTime'])+"\n")
    if startTime is not None or endTime is not None:
        startTimeFormated = datetime.datetime.fromtimestamp(startTime / 1000).strftime('%Y-%m-%d %H:%M:%S')
        endTimeFormated = datetime.datetime.fromtimestamp(endTime / 1000).strftime('%Y-%m-%d %H:%M:%S')
        file.write("start time: "+startTimeFormated+"\n"+"end time: "+endTimeFormated+"\n")
    print("===============================================")
    print("we are in timeframe: " + timeframe)
    print("previous candle time: "+str(df.iloc[-2]['OpenTime'])+"\n"+"current candle time: "+str(df.iloc[-1]['OpenTime']))
    #print(df)
    while True:
        lastKlines = instrument.getLastKlines()
        if lastKlines.iloc[1]['Close Time'] == endTime:
            endTimeFormated = datetime.datetime.fromtimestamp(endTime / 1000).strftime('%Y-%m-%d %H:%M:%S')
            file.write("end time: "+endTimeFormated+"\n")
            file.write("we hit the time limit\n")
            print("end time: "+endTimeFormated+"\n"+"we hit the time limit\n")
            break
        if df.iloc[-2]['Open Time'] == lastKlines.iloc[0]['Open Time'] and df.iloc[-1]['Open Time'] == lastKlines.iloc[1]['Open Time'] and newKlineAdded:
            df = BollingerBands(df)
            df = StochasticRSI(df)
            newKlineAdded = False
            signal = findSignal(df.iloc[-2]['c'], df.iloc[-1]['h'],df.iloc[-2]['l'], df.iloc[-2]['UpperBand'], df.iloc[-2]['LowerBand'], df.iloc[-2]['%K'], df.iloc[-2]['RSI'], file)
            if lowerTimeFrameList[timeframe] != "":
                isSignal(signal, df.iloc[-2]['c'],coinName,lowerTimeFrameList[timeframe],file, tradeList,
                         df.iloc[-1]['Open Time'], df.iloc[-1]['Close Time'], recurseAllowed=True)
        if df.iloc[-1]['Open Time'] != lastKlines.iloc[1]['Open Time']:
            # this operation is O(N) need to get addressed later
            df = df[:-1]
            df = df._append(lastKlines.iloc[0], ignore_index=True)
            df = df._append(lastKlines.iloc[1], ignore_index=True)
            newKlineAdded = True
        sleep(0.5)
    file.write("we come out of time frame:"+timeframe+"\n")
    file.write("================================================================")
    print("we come out of time frame:" + timeframe + "\n")
    print("================================================================")