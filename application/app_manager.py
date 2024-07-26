from contextlib import asynccontextmanager
import sys
from fastapi import FastAPI, APIRouter

from fastapi import applications
from fastapi.openapi.docs import get_swagger_ui_html

from loguru import logger

from db import db_helper


logger.add("file_1.log", colorize=True,
           format="<yellow>{time:YYYY-MM-DD at HH:mm:ss}</> | {level} | <level>{message}</>")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    logger.error("Движок бызы данных гарантированно закончил последнюю транзакцию и (*остановлен)")
    await db_helper.dispose()


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui.min.css")


applications.get_swagger_ui_html = swagger_monkey_patch


router = APIRouter()


@router.get('/ping')
async def ping() -> dict:
    return {"Success": "pong"}

