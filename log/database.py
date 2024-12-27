from log.utils import get_db_config
from pymongo import MongoClient
from enum import Enum
from typing import Union, List, Dict
from math import ceil


class InsertionType(Enum):
    SIMPLE = 0
    BULK = 1
    ONE_BY_ONE_BULK = 2


class MongoDB:
    def __init__(self) -> None:
        self.settings = get_db_config()
        self.init_db()
        self.init_collections()

    def init_db(self) -> None:
        self.db_connector = MongoClient(
            host=self.settings.DB_HOST, port=self.settings.DB_PORT
        )
        self.database = self.db_connector[self.settings.DB_NAME]

    def init_collections(self) -> None:
        self.logs = self.database[self.settings.LOG_COLLECTION_NAME]
        self.trades = self.database[self.settings.TRADE_COLLECTION_NAME]
        self.candles = self.database[self.settings.CANDLE_COLLECTION_NAME]
        self.collection_set = {
            "logs": self.logs,
            "trades": self.trades,
            "candles": self.candles,
        }

    def __del__(self):
        self.db_connector.close()

    def insert_to_collection(
        self,
        collection_name: str,
        data: Union[List, Dict],
        ordered: bool = False,
        insert_type: InsertionType = InsertionType.SIMPLE,
    ) -> bool:
        try:
            if collection_name not in self.collection_set:
                return False
            collection = self.collection_set[collection_name]
            if isinstance(data, list):
                if (
                    insert_type == InsertionType.BULK
                    or insert_type == InsertionType.SIMPLE
                ):
                    try:
                        if len(data) > 100:
                            return all(
                                [
                                    self.insert_to_collection(
                                        collection_name=collection_name,
                                        data=data[p * 100 : 100 * (p + 1)],
                                        insert_type=InsertionType.BULK,
                                    )
                                    for p in range(ceil(len(data) / 3))
                                ]
                            )
                        else:
                            collection.insert_many(documents=data, ordered=ordered)
                            return True
                    except:
                        return self.insert_to_collection(
                            collection_name=collection_name,
                            data=data,
                            insert_type=InsertionType.ONE_BY_ONE_BULK,
                        )
                else:
                    for record in data:
                        try:
                            collection.insert_one(document=record)
                        except:
                            ...
            else:
                collection.insert_one(document=data)
            return True
        except:
            return False
