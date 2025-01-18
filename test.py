import threading

import requests
from pandas import json_normalize
import pandas as pd
import numpy as np

from objects.Trade import Trade

instrumentList = ["EUR_USD", "EUR_CAD", "EUR_GBP", "XAU_USD", "XAG_USD"]
lowerTimeFrameList = {"M15": "M5", "M5":"M1", "M1": "S30", "S30": "S5", "S5": ""}
tradeList = []

def getChart(instrument,timeframe):
    url = 'https://api-fxpractice.oanda.com/v3/instruments/'+instrument+'/candles?price=M&smooth=True&granularity='+ timeframe +'&count=300'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 5ed1905fbb91438b6b990e9b67913f17-000250e17df04b6db52a166705a75018",
        "Accept-Datetime-Format": "UNIX"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print('Failed to retrieve data:', response.status_code)

def getChartToDate(instrument, timeframe, date):
    url = 'https://api-fxpractice.oanda.com/v3/instruments/'+instrument+'/candles?price=M&smooth=True&granularity=' + timeframe + '&count=1000' + '&to='+ str(date)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 5ed1905fbb91438b6b990e9b67913f17-000250e17df04b6db52a166705a75018",
        "Accept-Datetime-Format": "UNIX"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['granularity'] == timeframe:
            return data
    else:
        print('Failed to retrieve data:', response.status_code)



def jsonToPandas(data):
    df = json_normalize(data['candles'])

    # If you need to rename the columns to remove the 'mid.' prefix
    df.columns = [col.replace('mid.', '') for col in df.columns]

    # Convert the 'time' column to datetime
    df['time'] = pd.to_numeric(df['time'], errors='coerce')
    df['Time'] = pd.to_datetime(df['time'], unit='s')

    # Convert the price and volume data to appropriate numeric types
    df['c'] = pd.to_numeric(df['c'], errors='coerce')
    df['h'] = pd.to_numeric(df['h'], errors='coerce')
    df['l'] = pd.to_numeric(df['l'], errors='coerce')
    df['o'] = pd.to_numeric(df['o'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    return df


def BollingerBands(df, window=20, std_dev=2):
    """
    Calculates Bollinger Bands for a given DataFrame.

    Args:
        df: A pandas DataFrame with a 'Close' column.
        window: The window size for the SMA.
        std_dev: The number of standard deviations for the bands.

    Returns:
        A DataFrame with columns for the SMA, upper band, and lower band.
    """

    df['SMA'] = df['c'].rolling(window=window).mean()
    df['STD'] = df['c'].rolling(window=window).std(ddof=0)

    df['UpperBand'] = round(df['SMA'] + (df['STD'] * std_dev), 5)
    df['LowerBand'] = round(df['SMA'] - (df['STD'] * std_dev), 5)

    return df


def RSI(df, period=14):
    """
    Calculates the Relative Strength Index (RSI) for a given DataFrame.

    Args:
        df: A pandas DataFrame with a 'Close' column.
        period: The period for calculating RSI.

    Returns:
        A pandas Series containing the RSI values.
    """

    delta = df['c'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    exponentially_smoothed_gain = gain.ewm(com=period - 1, adjust=False).mean()
    exponentially_smoothed_loss = loss.ewm(com=period - 1, adjust=False).mean()
    RS = exponentially_smoothed_gain / exponentially_smoothed_loss
    RSI = round(100.0 - (100.0 / (1.0 + RS)), 4)
    return RSI

def StochasticRSI(df, rsi_period = 14, stoch_period = 14, k_period = 3, d_period = 3):
    """
    Calculates the Stochastic RSI for a given DataFrame.

    Args:
        df: A pandas DataFrame with a 'Close' column.
        period: The period for calculating the Stochastic Oscillator.
        smooth_window: The window for smoothing the %K line.

    Returns:
        A pandas DataFrame with the Stochastic RSI values.
    """

    df['RSI'] = RSI(df, rsi_period)
    #
    # # Calculate %K
    # df['%K'] = round((df['RSI'] - df['RSI'].rolling(window=period).min()) / (
    #             df['RSI'].rolling(window=period).max() - df['RSI'].rolling(window=period).min()) * 100, 4)
    #
    # # Calculate %D (Smooth %K)
    # df['%D'] = df['%K'].rolling(window=smooth_window).mean()

    # Calculate StochRSI
    min_rsi = df['RSI'].rolling(window=stoch_period, min_periods=stoch_period).min()
    max_rsi = df['RSI'].rolling(window=stoch_period, min_periods=stoch_period).max()
    stoch_rsi = (df['RSI'] - min_rsi) / (max_rsi - min_rsi)

    # Calculate %K
    df['%K'] = round(stoch_rsi.rolling(window=k_period, min_periods=k_period).mean(), 4) * 100

    # Calculate %D
    df['%D'] = round(df['%K'].rolling(window=d_period, min_periods=d_period).mean(), 4)

    return df

def findRSIDivergence():
    pass

def findSignal(closePrice,highPrice,lowPrice, upper_band, lower_band, stochRSIK, rsi, entryTime):
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

def showTradeProfit(tradeList):
    profit = 0
    lostProfit = 0
    for trade in tradeList:
        if trade.isComplete and trade.profit > 0:
            profit += trade.profit
        elif trade.isComplete and trade.profit < 0:
            profit += trade.profit
            lostProfit += trade.profit
    return profit, lostProfit


def marketSimulator(chart, instrument, timeFrame, file, tradeList, startTime=None,limit=None):
    try:
        file.write("===============================================\n")
        file.write("we are in timeframe: "+ timeFrame+"\n")
        file.write("chart start at: " + str(chart['Time'].iloc[0]) + "chart ends at:" + str(chart['Time'].iloc[len(chart['Time'])-1])+"\n")
        print("===============================================")
        print("we are in timeframe: ", timeFrame)
        print("chart start at: " + str(chart['Time'].iloc[0]) + "chart ends at:" + str(chart['Time'].iloc[len(chart['Time'])-1]))
        signal_found = False
        for index, row in chart.iterrows():
            if startTime is not None:
                if row['time'] < startTime:
                    continue
            print("############################################")
            print("Time is: "+str(row['Time'])+" timeframe is: "+timeFrame)
            if row['time'] == 1734685740.0:
                print("found you")
            candle = row['c']
            if( index + 1 < len(chart) ):
                nextCandleTime= chart['time'].iloc[index + 1]
                print("next candle time: ",chart['Time'].iloc[index + 1])
            else:
                nextCandleTime = row['time']
            upper_band = row['UpperBand']
            lower_band = row['LowerBand']
            d = row['%D']
            k = row['%K']
            rsi = row['RSI']
            file.write("##########################################\n")
            print("candle price: " + str(candle)+" RSI: " + str(rsi) + " stochRSI: " + str(k)+ " "+str(d)+" upper bond: " + str(upper_band)+" lower bond: " + str(lower_band))
            file.write("Time is: "+str(row['Time'])+" timeframe is: "+timeFrame+"\n"+ "candle price: " + str(candle)+" RSI: " + str(rsi) + " stochRSI: " + str(k)+ " "+str(d)+" upper bond: " + str(upper_band)+" lower bond: " + str(lower_band)+"\n")
            signalType = findSignal(row['c'],row['h'],row['l'], upper_band, lower_band, k, rsi, row['Time'])
            file.write("signal type: "+signalType+"\n")
            file.write("time in unix: "+str(row['time'])+" signal found: "+str(signal_found)+"\n")
            if signalType == "SELL":
                trade = Trade("SELL", row['c'], row['Time'], False)
                if len(tradeList) > 0:
                    for currentTrade in tradeList:
                        if not currentTrade.isComplete and currentTrade.tradeSide == "BUY":
                            currentTrade.isComplete = True
                            currentTrade.priceExit = row['c']
                            currentTrade.setProfit()
                tradeList.append(trade)
                file.write("SELL\n")
                print("Time: "+str(row['Time'])+" SELL")
                signal_found = True
            elif signalType == "BUY":
                trade = Trade("BUY", row['c'], row['Time'], False)
                if len(tradeList) > 0:
                    for currentTrade in tradeList:
                        if not currentTrade.isComplete and currentTrade.tradeSide == "SELL":
                            currentTrade.isComplete = True
                            currentTrade.priceExit = row['c']
                            currentTrade.setProfit()

                tradeList.append(trade)
                file.write("BUY\n")
                print("Time: "+str(row['Time'])+" BUY")
                signal_found = True
            elif signalType == "PARTIAL" and not signal_found:
                if lowerTimeFrameList[timeFrame] in lowerTimeFrameList:
                    file.write("PARTIAL\n")
                    print("time is: "+str(row['Time'])+" we are going from timeframe: "+timeFrame+" to timeframe: "+lowerTimeFrameList[timeFrame])
                    newChart = getChartToDate(instrument, lowerTimeFrameList[timeFrame],nextCandleTime)
                    df = jsonToPandas(newChart)
                    df = BollingerBands(df)
                    df = StochasticRSI(df)
                    marketSimulator(df, instrument,lowerTimeFrameList[timeFrame], file, tradeList, row['time'], nextCandleTime)
            elif row['time'] == limit:
                file.write("we hit the time limit\n")
                print("we hit the limit")
                break
        file.write("=====================================\n")
    except KeyError as e:
        print(f"Error: Missing column '{e.args[0]}' in DataFrame.")


threads = []
fileList = []

for instrument in instrumentList:
    file = open(instrument+"_log.txt", "w")
    fileList.append(file)
    oneMinutechart = getChart(instrument, 'M5')
    oneMinutedf = jsonToPandas(oneMinutechart)
    oneMinutedf = BollingerBands(oneMinutedf)
    oneMinutedf = StochasticRSI(oneMinutedf)
    tradeList = []

        # Create the thread and pass the file object
    thread = threading.Thread(target=marketSimulator, args=(oneMinutedf, instrument, "M5", file, tradeList))
    threads.append(thread)
    thread.start()

    # print("====================="+instrument+"==================================")
    # print("profit is: {0}\nlost profit is: {1}".format(showTradeProfit(tradeList)[0], showTradeProfit(tradeList)[1]))
    # for trade in tradeList:
    #     print("trade time: "+str(trade.entryTime)+" "+ trade.tradeSide+" trade entry price: "+str(trade.priceEntry)+" trade exit price: "+str(trade.priceExit)+" trade profit: "+str(trade.profit))
    #
    # print("=====================================================================")


for thread in threads:
    thread.join()

for file in fileList:
    file.close()




