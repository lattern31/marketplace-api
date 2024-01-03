from envparse import Env
import pathlib
from pydantic_settings import BaseSettings


BASE_DIR = pathlib.Path(__file__).parent.parent

env = Env()
env.read_envfile(BASE_DIR / '.env')


class Settings(BaseSettings):
    echo: bool = env.bool("ECHO", default=False)
    postgres_host: str = env.str("POSTGRES_HOST")
    postgres_port: int = env.int("POSTGRES_PORT")
    postgres_db: str = env.str("POSTGRES_DB")
    postgres_user: str = env.str("POSTGRES_USER")
    postgres_password: str = env.str("POSTGRES_PASSWORD")
    db_string: str = (
        "postgresql+asyncpg://"
        f"{postgres_user}:{postgres_password}"
        f"@{postgres_host}:{postgres_port}"
        f"/{postgres_db}"
    )


settings = Settings()

