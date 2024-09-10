import dotenv
import pathlib


BASE_DIR = pathlib.Path(__file__).parent.parent


dotenv.load_dotenv(BASE_DIR)

class Settings:
    secret_key = dotenv.dotenv_values().get("SECRET_KEY", "SECRET_KEY_FOR_CI")
    debug = dotenv.dotenv_values().get("DEBUG", False)
    access_token_expire_minutes = dotenv.dotenv_values().get(
        "ACCESS_TOKEN_EXPIRE_MINUTES", 15
    )
    algorithm = dotenv.dotenv_values().get("ALGORITHM", 'HS256')
    postgres_host = dotenv.dotenv_values().get("POSTGRES_HOST", "localhost")
    postgres_port = dotenv.dotenv_values().get("POSTGRES_PORT", 5432)
    postgres_db = dotenv.dotenv_values().get("POSTGRES_DB", "postgres")
    postgres_user = dotenv.dotenv_values().get("POSTGRES_USER", "postgres")
    postgres_password = dotenv.dotenv_values().get("POSTGRES_PASSWORD", "postgres")
    db_string: str = (
        "postgresql+asyncpg://"
        f"{postgres_user}:{postgres_password}"
        f"@{postgres_host}:{postgres_port}/{postgres_db}"
    )
    postgres_test_port = dotenv.dotenv_values().get(
        "POSTGRES_TEST_PORT", 5433
    )
    db_test_string: str = (
        "postgresql+asyncpg://"
        f"{postgres_user}:{postgres_password}"
        f"@{postgres_host}:{postgres_test_port}/postgres"
    )


settings = Settings
