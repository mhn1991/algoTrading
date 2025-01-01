from objects.Trade import Trade
from Brokers.Binance.run import run

def findSignal(closePrice,highPrice,lowPrice, upper_band, lower_band, stochRSIK, rsi) -> str:
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


def isSignal(signal: str, marketPrice,coinName, timeframe, file, tradeList, startTime=None, endTime=None):
    if signal == "SELL":
        trade = Trade("SELL", marketPrice, startTime, False)
        closeTrades("Buy", tradeList, marketPrice)
        tradeList.append(trade)
        file.write("##########################################\nSELL\n")
        file.write("we are in timeframe: " + timeframe + "\n")
        file.write("we are in timeframe: " + timeframe + "\n")
    elif signal == "BUY":
        trade = Trade("BUY", marketPrice, startTime, False)
        closeTrades("Sell", tradeList, marketPrice)
        tradeList.append(trade)
    elif signal == "PARTIAL":
        run(coinName, timeframe, file, tradeList, startTime, endTime)


def closeTrades(signal, tradeList, price):
    if len(tradeList) > 0:
        for currentTrade in tradeList:
            if not currentTrade.isComplete and currentTrade.tradeSide == signal:
                currentTrade.isComplete = True
                currentTrade.priceExit = price
                currentTrade.setProfit()