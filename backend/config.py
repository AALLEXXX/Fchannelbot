from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:
    bot_token: str
    admin_id: int


@dataclass
class Settings:
    bots: Bots
    DB_SQLITE_PATH: str
    REDIS_HOST: str
    REDIS_PORT: str
    channel_id:int
    test_channel_id:int

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    ADMIN_ID: int

    @property
    def DATABASE_URL_SQLITE(self) -> str:
        return f"sqlite+aiosqlite:///{self.DB_SQLITE_PATH}"

    @property
    def DATABASE_URL_POSTGRES(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


def get_settings(path: str) -> Settings:
    env = Env()
    env.read_env(path)

    print("Loaded .env file:", path)
    print("TOKEN:", env.str("TOKEN", "Not Found"))
    print("ADMIN_ID:", env.int("ADMIN_ID", "Not Found"))

    return Settings(
        bots=Bots(bot_token=env.str("TOKEN"), admin_id=env.int("ADMIN_ID")),
        DB_SQLITE_PATH=env.str("DB_SQLITE_PATH"),
        REDIS_HOST=env.str("REDIS_HOST"),
        REDIS_PORT=env.str("REDIS_PORT"),
        channel_id=env.int("CHANNEL_ID"),
        test_channel_id=env.int("TEST_CHANNEL_ID"),
        ADMIN_ID=env.int('ADMIN_ID'),
        DB_HOST=env.str('DB_HOST'),
        DB_NAME=env.str('DB_NAME'),
        DB_PASS=env.str('DB_PASS'),
        DB_PORT=env.str('DB_PORT'),
        DB_USER=env.str('DB_USER')
    )


settings: Settings = get_settings(".env")