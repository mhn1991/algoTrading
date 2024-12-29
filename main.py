from Brokers.Oanda.instrument import Instrument
from Brokers.Binance.instrument import Instrument as BinanceInstrument
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

if __name__ == "__main__":
    binanceTest()