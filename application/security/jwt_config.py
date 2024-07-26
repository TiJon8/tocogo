from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenType(BaseSettings):
    TOKEN_TYPE_FIELD: str = "type"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"


class TokenConfig(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 30
    REFRESH_TOKEN_EXPIRE: int = 30

    type: TokenType = TokenType()

    model_config = SettingsConfigDict(env_file='.env_security_token')


jwt_config = TokenConfig()