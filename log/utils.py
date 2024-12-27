from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    LOG_COLLECTION_NAME: str
    TRADE_COLLECTION_NAME: str
    CANDLE_COLLECTION_NAME: str

    class Config:
        env_file = ".db_env"
        env_file_encoding = "utf-8"


class FileSettings(BaseSettings):
    FILE_PATH: str
    FILE_NAME: str

    class Config:
        env_file = ".file_env"
        env_file_encoding = "utf-8"


def get_db_config():
    return DBSettings()


def get_file_config():
    return FileSettings()
