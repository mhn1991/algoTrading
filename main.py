from Brokers.Oanda.instrument import Instrument


def main():
    instrument = Instrument('EUR_USD')
    df = instrument.getChart('practice', 'M5')
    print(df)

if __name__ == "__main__":
    main()