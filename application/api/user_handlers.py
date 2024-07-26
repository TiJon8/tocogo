from uuid import UUID

from fastapi import APIRouter, Request, Response, Depends
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from extentions import ERROR_403_FORBIDDEN, ERROR_406_NOT_ACCEPTABLE
from .crud import _delete_user, _get_user, _update_user
from .models import (ShowUser, UpdateUserRequest, ShowComposite, ShowTask, UserID)
from .actions import check_cookies, check_user_permissions
from application.db import PortalRoles, db_helper


router = APIRouter()


@router.get('/', response_model=ShowUser, response_model_exclude_none=False)
async def get_user(user_id: UUID,
                   request: Request,
                   response: Response,
                   session: AsyncSession = Depends(db_helper.session_getter)) -> ShowUser:

    current_user = await check_cookies(request=request, response=response, session=session)
    user = await _get_user(user_id=user_id, session=session)
    if user.user_id != current_user.user_id:
        raise ERROR_403_FORBIDDEN

    composites = [ShowComposite.model_validate(row, from_attributes=True) for row in user.composites]
    tasks = [ShowTask.model_validate(row, from_attributes=True) for row in user.tasks]

    # return ShowUser.model_validate(user, from_attributes=True)

    a = ShowUser(
        user_id=user.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email=user.email,
        is_active=user.is_active,
        composites=composites,
        tasks=tasks
    )

    return a


@router.delete('/', response_model=UserID)
async def delete_user(user_id: UUID,
                      request: Request,
                      response: Response,
                      session: AsyncSession = Depends(db_helper.session_getter)) -> UserID:

    current_user = await check_cookies(request=request, response=response, session=session)

    user_for_deletion = await _get_user(user_id=user_id, session=session)
    if PortalRoles.ROLE_PORTAL_OWNER in current_user.roles:
        raise ERROR_406_NOT_ACCEPTABLE
    if not check_user_permissions(
        target_user=user_for_deletion,
        current_user=current_user
    ):
        raise ERROR_403_FORBIDDEN
    deleted_user_id = await _delete_user(user_id=user_id, session=session)
    return UserID(user_id=deleted_user_id)


@router.patch('/', response_model=UserID)
async def patch_user(user_id: UUID,
                     body: UpdateUserRequest,
                     request: Request,
                     response: Response,
                     session: AsyncSession = Depends(db_helper.session_getter)) -> UserID:

    current_user = await check_cookies(request=request, response=response, session=session)

    updated_params = body.dict(exclude_none=True)
    if updated_params == {}:
        raise HTTPException(status_code=422, detail=f'Должен быть передан хотябы 1 аргумент')

    user = await _get_user(user_id=user_id, session=session)
    if not check_user_permissions(
            target_user=user,
            current_user=current_user
    ):
        raise ERROR_403_FORBIDDEN

    updated_user = await _update_user(user_id=user_id, updated_params=updated_params, session=session)
    return UserID(user_id=updated_user)
