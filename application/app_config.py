from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RunAppSettings(BaseModel):
    HOST: str = "0.0.0.0"
    PORT: int = 8000


class APIv1Settings(BaseModel):
    BASE_API_URL: str = "/api/v1"
    USER: str = "/user"
    AUTH: str = "/auth"
    COMPOSITE: str = "/composite"
    TASK: str = "/task"
    ADMIN_PANEL: str = "/admin"


class AppConfig(BaseSettings):
    run: RunAppSettings = RunAppSettings()
    api: APIv1Settings = APIv1Settings()


app_config = AppConfig()
