from API.REST.client import Client
import pandas as pd

class Instrument:
    def __init__(self, coinName, timeFrame):
        self.coinName = coinName
        self.timeFrame = timeFrame
        self.client = Client()

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
        uri = "https://api.binance.com/" + "api/v3/klines"+"?symbol="+self.coinName+"&interval="+self.timeFrame
        jsonData = self.client.get(uri, {})
        df = self.jsonToPandas(jsonData)
        return df

    def getLastKlines(self):
        uri = "https://api.binance.com/" + "api/v3/klines" + "?symbol="+self.coinName+"&interval="+self.timeFrame+"&limit=2"
        jsonData = self.client.get(uri, {})
        df = self.jsonToPandas(jsonData)
        return df