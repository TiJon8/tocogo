from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from api import main_api_router
from app_manager import lifespan
from app_config import app_config
from app_manager import router as ping_router


""" FastAPI APPLICATION """


app = FastAPI(title="FastAPI", description="Fastapi Interface Document", version="1.0.0",
              default_response_class=ORJSONResponse,
              lifespan=lifespan)


app.include_router(ping_router)
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host=app_config.run.HOST, port=app_config.run.PORT)
