from Brokers.Binance.instrument import Instrument as BinanceInstrument
from Analysis.Indicators.indicators import BollingerBands,StochasticRSI
from time import sleep
import numpy as np


# I need better logic than sleep probably checking if the time is more than the close time of the last candle then execute
def run():
    instrument = BinanceInstrument('EUR_USD')
    df = instrument.getChart()
    df = BollingerBands(df)
    df = StochasticRSI(df)
    newKlineAdded = False
    print(df)
    while True:
        lastKlines = instrument.getLastKlines()
        if df.iloc[-2]['Open Time'] == lastKlines.iloc[0]['Open Time'] and df.iloc[-1]['Open Time'] == lastKlines.iloc[1]['Open Time'] and newKlineAdded:
            df = BollingerBands(df)
            df = StochasticRSI(df)
            newKlineAdded = False
            print(df.tail(2))
        if df.iloc[-1]['Open Time'] != lastKlines.iloc[1]['Open Time']:
            df = df[:-1]
            df = df._append(lastKlines.iloc[0], ignore_index=True)
            df = df._append(lastKlines.iloc[1], ignore_index=True)
            newKlineAdded = True
        sleep(1)

    # print(df)

def main():
    run()