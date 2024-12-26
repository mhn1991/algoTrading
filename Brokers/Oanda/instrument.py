import pandas as pd

from pandas import json_normalize
from API.REST.client import Client
from Brokers.Oanda.config import Config


class Instrument:
    def __init__(self, symbol):
        self.symbol = symbol

    def jsonToPandas(self, data):
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

    def getChart(self, accountType, timeFrame):
        client = Client()
        if accountType == "practice":
            config = Config()
            jsonData = client.get(config.practiceURL, config.headers)
            return self.jsonToPandas(jsonData)
        elif accountType == "real":
            config = Config()
            jsonData = client.get(config.tradeURL, config.headers)
            return self.jsonToPandas(jsonData)