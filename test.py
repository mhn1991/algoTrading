import requests
from pandas import json_normalize
import pandas as pd
import matplotlib.pyplot as plt
import talib as ta

from objects.Trade import Trade

lowerTimeFrameList = {"M15": "M5", "M5":"M1", "M1": "S15"}
tradeList = []

def getChart(timeframe):
    url = 'https://api-fxpractice.oanda.com/v3/instruments/EUR_USD/candles?price=M&smooth=True&granularity='+ timeframe +'&count=300'
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

def getChartToDate(timeframe, date):
    url = 'https://api-fxpractice.oanda.com/v3/instruments/EUR_USD/candles?price=M&smooth=True&granularity=' + timeframe + '&count=300' + '&to='+ str(date)
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
    df['STD'] = df['c'].rolling(window=window).std()

    df['UpperBand'] = round(df['SMA'] + (df['STD'] * std_dev), 4)
    df['LowerBand'] = round(df['SMA'] - (df['STD'] * std_dev), 4)

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

def StochasticRSI(df, period=14, smooth_window=3):
    """
    Calculates the Stochastic RSI for a given DataFrame.

    Args:
        df: A pandas DataFrame with a 'Close' column.
        period: The period for calculating the Stochastic Oscillator.
        smooth_window: The window for smoothing the %K line.

    Returns:
        A pandas DataFrame with the Stochastic RSI values.
    """

    df['RSI'] = RSI(df, period)

    # Calculate %K
    df['%K'] = round((df['RSI'] - df['RSI'].rolling(window=period).min()) / (
                df['RSI'].rolling(window=period).max() - df['RSI'].rolling(window=period).min()) * 100, 4)

    # Calculate %D (Smooth %K)
    df['%D'] = df['%K'].rolling(window=smooth_window).mean()

    return df



def findSignal(candle, upper_band, lower_band, stochRSIK, rsi, entryTime):
    print("####time is: " + str(entryTime))
    # base case for set up a sell trade
    if candle >= upper_band and stochRSIK == 100.0 and rsi > 70.0:
        trade = Trade("SELL", candle, entryTime, False)
        if len(tradeList) > 0:
            for currentTrade in tradeList:
                if not currentTrade.isComplete and currentTrade.tradeSide == "BUY":
                    currentTrade.isComplete = True
                    currentTrade.priceExit = candle
                    currentTrade.setProfit()
        tradeList.append(trade)
        return "SELL"
    #base case for set up a buy trade
    if candle <= lower_band and stochRSIK == 0.0 and rsi < 28.0:
        trade = Trade("BUY", candle, entryTime, False)
        if len(tradeList) > 0:
            for currentTrade in tradeList:
                if not currentTrade.isComplete and currentTrade.tradeSide == "BUY":
                    currentTrade.isComplete = True
                    currentTrade.priceExit = candle
                    currentTrade.setProfit()

        tradeList.append(trade)
        return "BUY"

    # here we satisfied partially so we are going to a smaller time frame
    if (candle >= upper_band and stochRSIK > 85) or (candle <= lower_band and stochRSIK < 15):
        return "PARTIAL"

def showTradeProfit():
    profit = 0
    lostProfit = 0
    for trade in tradeList:
        if trade.isComplete and trade.profit > 0:
            profit += trade.profit
        elif trade.isComplete and trade.profit < 0:
            profit += trade.profit
            lostProfit += trade.profit
    return profit, lostProfit


def marketSimulator(chart, timeFrame, startTime=None,limit=None):
    try:
        with open('log.txt', 'w') as file:
            file.write("===============================================\n")
            file.write("we are in timeframe: "+ timeFrame+"\n")
            file.write("chart start at: " + str(chart['Time'].iloc[0]) + "chart ends at:" + str(chart['Time'].iloc[len(chart['Time'])-1]))
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
                candle = row['c']
                if( index + 1 < len(chart) ):
                    nextCandleTime= chart['time'].iloc[index + 1]
                    print("next candle time: ",chart['Time'].iloc[index + 1])
                upper_band = row['UpperBand']
                lower_band = row['LowerBand']
                d = row['%D']
                k = row['%K']
                rsi = row['RSI']
                print("candle price: " + str(candle)+" RSI: " + str(rsi) + " stochRSI: " + str(k)+ " "+str(d)+" upper bond: " + str(upper_band)+" lower bond: " + str(lower_band))
                signalType = findSignal(candle, upper_band, lower_band, k, rsi, row['Time'])
                if signalType == "SELL":
                    print("Time: "+str(row['Time'])+" SELL")
                    signal_found = True
                elif signalType == "BUY":
                    print("Time: "+str(row['Time'])+" BUY")
                    signal_found = True
                elif signalType == "PARTIAL" and not signal_found:
                    if lowerTimeFrameList[timeFrame] in lowerTimeFrameList:
                        print("time is: "+str(row['Time'])+" we are going from timeframe: "+timeFrame+" to timeframe: "+lowerTimeFrameList[timeFrame])
                        newChart = getChartToDate(lowerTimeFrameList[timeFrame],nextCandleTime)
                        df = jsonToPandas(newChart)
                        df = BollingerBands(df)
                        df = StochasticRSI(df)
                        marketSimulator(df, lowerTimeFrameList[timeFrame], row['time'], nextCandleTime)
                elif row['time'] == limit:
                    file.write("we hit the time limit\n")
                    print("we hit the limit")
                    break
    except KeyError as e:
        print(f"Error: Missing column '{e.args[0]}' in DataFrame.")



oneMinutechart = getChart('M5')
oneMinutedf = jsonToPandas(oneMinutechart)
oneMinutedf = BollingerBands(oneMinutedf)
oneMinutedf = StochasticRSI(oneMinutedf)

marketSimulator(oneMinutedf, "M5")
print("profit is: {0}\nlost profit is: {1}".format(showTradeProfit()[0]*10000, showTradeProfit()[1]*10000))
for trade in tradeList:
    print("trade time: "+str(trade.entryTime)+" "+ trade.tradeSide+" trade entry price: "+str(trade.priceEntry)+" trade exit price: "+str(trade.priceExit)+" trade profit: "+str(trade.profit))

tradeList.clear()
exit(0)
fiveMinutedf = BollingerBands(fiveMinutedf)
fiveMinutedf = StochasticRSI(fiveMinutedf)






plt.figure(figsize=(12, 8))

# Plot the main price chart with Bollinger Bands
plt.subplot(2, 1, 1)
plt.plot(oneMinutedf['time'], oneMinutedf['c'], label='Price')
plt.plot(oneMinutedf['time'], oneMinutedf['UpperBand'], color='red', label='Upper Band')
plt.plot(oneMinutedf['time'], oneMinutedf['LowerBand'], color='red', label='Lower Band')
plt.fill_between(oneMinutedf['time'], oneMinutedf['UpperBand'], oneMinutedf['LowerBand'], color='gray', alpha=0.2)
plt.title('Price Chart with Bollinger Bands')
plt.ylabel('Price')
plt.xlabel('Time')

# Plot the Stochastic RSI on a separate subplot
plt.subplot(2, 1, 2)
plt.plot(oneMinutedf['time'], oneMinutedf['%K'], color='blue', label='%K')
plt.plot(oneMinutedf['time'], oneMinutedf['%D'], color='orange', label='%D')
plt.axhline(80, color='black', linestyle='--')
plt.axhline(20, color='black', linestyle='--')
plt.title('Stochastic RSI')
plt.ylabel('RSI')
plt.xlabel('Time')
plt.legend()

plt.tight_layout()
plt.show()





