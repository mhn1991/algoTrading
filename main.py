from time import sleep

from Brokers.Oanda.instrument import Instrument
from Brokers.Binance.instrument import Instrument as BinanceInstrument
from Brokers.Binance.run import run
from Analysis.Indicators.indicators import *


def oandaTest():
    instrument = Instrument('EUR_USD')
    df = instrument.getChart('practice', 'M5')
    print(df)

def binanceTest():
    instrument = BinanceInstrument('EUR_USD')
    df = instrument.getChart()
    df = BollingerBands(df)
    df = StochasticRSI(df)
    print(df)
    while True:
        lastKlines = instrument.getLastKlines()
        print(lastKlines.iloc[1]['OpenTime'])
        if df.iloc[-1]['Open Time'] != lastKlines.iloc[1]['Open Time']:
            print(lastKlines.iloc[1]['OpenTime'])
            df = df._append(lastKlines.iloc[1], ignore_index=True)
            break
        sleep(5)

    print(df)
if __name__ == "__main__":
    file = open('./files/logs/BTCUSDT.txt', 'w')
    tradeList = []
    run("BTCUSDT","5m", file,tradeList)
    file.close()