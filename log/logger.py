import logging.handlers
from log.database import MongoDB
import logging


class Logger(logging.Formatter):
    def __init__(self, format):
        super().__init__(fmt=format)
        self.database = MongoDB()

    def format(self, record):
        log_message = super().format(record)
        self.write_log(log_message)
        return log_message

    def write_log(self, log: str):
        try:
            self.database.insert_to_collection(
                collection_name="logs", data={"log": log}
            )
        except:
            ...


handler = logging.StreamHandler()
handler.setFormatter(
    Logger("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
)
logging.basicConfig(level=logging.NOTSET, handlers=[handler], encoding="utf-8")
