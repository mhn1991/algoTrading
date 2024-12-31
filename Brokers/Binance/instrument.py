from API.REST.client import Client
import pandas as pd

class Instrument:
    def __init__(self, symbol):
        self.symbol = symbol

    def jsonToPandas(self, json):
        columns = ['Open Time', 'o', 'h', 'l', 'c', 'Volume',
                   'Close Time', 'Quote Asset Volume', 'Number of Trades',
                   'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore']

        df = pd.DataFrame(json, columns=columns)

        # Convert 'Open Time' and 'Close Time' to datetime
        df['OpenTime'] = pd.to_datetime(df['Open Time'], unit='ms')
        df['CloseTime'] = pd.to_datetime(df['Close Time'], unit='ms')

        # Convert numerical columns to appropriate data types
        for col in ['o', 'h', 'l', 'c', 'Volume', 'Quote Asset Volume',
                    'Number of Trades', 'Taker Buy Base Asset Volume',
                    'Taker Buy Quote Asset Volume']:
            df[col] = pd.to_numeric(df[col])
        return df

    def getChart(self):
        client = Client()
        uri = "https://api.binance.com/" + "api/v3/klines"+"?symbol=BTCUSDT&interval=1m"
        jsonData = client.get(uri, {})
        df = self.jsonToPandas(jsonData)
        return df

    def getLastKlines(self):
        client = Client()
        uri = "https://api.binance.com/" + "api/v3/klines" + "?symbol=BTCUSDT&interval=1m&limit=2"
        jsonData = client.get(uri, {})
        df = self.jsonToPandas(jsonData)
        return df