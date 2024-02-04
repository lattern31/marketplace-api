from envparse import Env
import pathlib
from pydantic_settings import BaseSettings


BASE_DIR = pathlib.Path(__file__).parent.parent

env = Env()
env.read_envfile(BASE_DIR / '.env')


class Settings(BaseSettings):
    debug: bool = env.bool("DEBUG", default=False)
    postgres_host: str = env.str("POSTGRES_HOST", default="localhost")
    postgres_port: int = env.int("POSTGRES_PORT", default=5432)
    postgres_db: str = env.str("POSTGRES_DB", default="postgres")
    postgres_user: str = env.str("POSTGRES_USER", default="postgres")
    postgres_password: str = env.str("POSTGRES_PASSWORD", default="postgres")
    db_string: str = (
        "postgresql+asyncpg://"
        f"{postgres_user}:{postgres_password}"
        f"@{postgres_host}:{postgres_port}/{postgres_db}"
    )
    postgres_test_port: int = env.int("POSTGRES_TEST_PORT", default=5433)
    db_test_string: str = (
        "postgresql+asyncpg://"
        f"{postgres_user}:{postgres_password}"
        f"@{postgres_host}:{postgres_test_port}/postgres"
    )


settings = Settings()

