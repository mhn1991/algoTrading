from Analysis.Indicators.signalFactory import findSignal, isSignal
from Brokers.Binance.instrument import Instrument as BinanceInstrument
from Analysis.Indicators.indicators import BollingerBands,StochasticRSI
from time import sleep
import numpy as np
lowerTimeFrameList = {"15m": "5m", "5m":"1m", "1m": "1s", "1s": ""}

# I need better logic than sleep probably checking if the time is more than the close time of the last candle then execute
def run(coinName, timeframe, file, tradeList, startTime=None, endTime=None):
    file.write("===============================================\n")
    file.write("we are in timeframe: " + timeframe + "\n")
    instrument = BinanceInstrument(coinName, timeframe)
    df = instrument.getChart()
    df = BollingerBands(df)
    df = StochasticRSI(df)
    newKlineAdded = False
    #print(df)
    while True:
        lastKlines = instrument.getLastKlines()
        if df.iloc[-2]['Open Time'] == lastKlines.iloc[0]['Open Time'] and df.iloc[-1]['Open Time'] == lastKlines.iloc[1]['Open Time'] and newKlineAdded:
            df = BollingerBands(df)
            df = StochasticRSI(df)
            newKlineAdded = False
            signal = findSignal(df.iloc[-2]['c'], df.iloc[-1]['h'],df.iloc[-2]['l'], df.iloc[-2]['UpperBand'], df.iloc[-2]['LowerBand'], df.iloc[-2]['%K'], df.iloc[-2]['RSI'])
            isSignal(signal, df.iloc[-2]['c'],coinName,lowerTimeFrameList[timeframe],file, tradeList,
                     df.iloc[-2]['Open Time'], df.iloc[-2]['Close Time'])
        if df.iloc[-1]['Open Time'] != lastKlines.iloc[1]['Open Time']:
            # this operation is O(N) need to get addressed later
            df = df[:-1]
            df = df._append(lastKlines.iloc[0], ignore_index=True)
            df = df._append(lastKlines.iloc[1], ignore_index=True)
            newKlineAdded = True
        sleep(1)

    # print(df)
