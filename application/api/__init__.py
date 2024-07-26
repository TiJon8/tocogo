from fastapi import APIRouter
from app_config import app_config

from .user_handlers import router as user_router
from .auth_handlers import router as auth_router
from .manager_handlers import router as manager_router
from .composite_handlers import router as composite_router
from .task_handlers import router as task_router


__all__ = "main_api_router"


main_api_router = APIRouter()


main_api_router.include_router(user_router,
                               prefix=f'{app_config.api.BASE_API_URL}{app_config.api.USER}',
                               tags=['user-api-v1'])
main_api_router.include_router(auth_router, prefix=f'{app_config.api.BASE_API_URL}{app_config.api.AUTH}',
                               tags=['auth-api-v1'])

main_api_router.include_router(composite_router, prefix=f'{app_config.api.BASE_API_URL}{app_config.api.COMPOSITE}',
                               tags=['composite-api-v1'])
main_api_router.include_router(task_router, prefix=f'{app_config.api.BASE_API_URL}{app_config.api.TASK}',
                               tags=['task-api-v1'])

main_api_router.include_router(manager_router, prefix=f'{app_config.api.BASE_API_URL}{app_config.api.ADMIN_PANEL}',
                               tags=['admin-api-v1'])
