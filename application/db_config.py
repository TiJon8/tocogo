from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class DatabaseURLConfig(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_psycopg(self) -> PostgresDsn:
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def DATABASE_URL_alembic(self) -> PostgresDsn:
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=False, env_ignore_empty=True)


class DatabaseEngineConfig(BaseSettings):
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 10
    max_overflow: int = 5


class SQLAlchemyConfig(BaseSettings):

    naming_conventions: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }


db_url_config = DatabaseURLConfig()
db_engine_config = DatabaseEngineConfig(echo=True, pool_size=50, max_overflow=10)
sqlalchemy_config = SQLAlchemyConfig()
