from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from psycopg import IntegrityError

from extentions import ERROR_401_UNAUTHORIZED, ERROR_403_FORBIDDEN, ERROR_409_CONFLICT
from .actions.auth import get_user_from_token
from .crud import _get_user, _update_user
from .models import UserID
from application.db import db_helper


router = APIRouter()


@router.patch('/privilege', response_model=UserID)
async def add_admin_privilege(user_id: UUID, request: Request, response: Response,
                              session: AsyncSession = Depends(db_helper.session_getter)):
    if not request.cookies.get("xww-access-cookie") and not request.cookies.get("xws-security-cookie"):
        raise ERROR_401_UNAUTHORIZED
    access_token = request.cookies.get("xww-access-cookie")
    refresh_token = request.cookies.get("xws-security-cookie")
    current_user = await get_user_from_token(access_token=access_token, refresh_token=refresh_token, response=response,
                                             session=session)
    if not current_user.is_owner:
        raise ERROR_403_FORBIDDEN
    user_for_promotion = await _get_user(user_id=user_id, session=session)
    if user_for_promotion.is_admin:
        raise ERROR_409_CONFLICT

    if user_for_promotion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id!r} not found")

    updated_user_params = {
        "roles": user_for_promotion.enrich_admin_role()
    }
    try:
        updated_user_id = await _update_user(user_id=user_id, updated_params=updated_user_params, session=session)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Error on database side')
    return UserID(user_id=updated_user_id)


@router.delete('/privilege', response_model=UserID)
async def revoke_admin_privilege(user_id: UUID, request: Request, response: Response,
                                 session: AsyncSession = Depends(db_helper.session_getter)):
    if not request.cookies.get("xww-access-cookie") and not request.cookies.get("xws-security-cookie"):
        raise ERROR_401_UNAUTHORIZED
    access_token = request.cookies.get("xww-access-cookie")
    refresh_token = request.cookies.get("xws-security-cookie")
    current_user = await get_user_from_token(access_token=access_token, refresh_token=refresh_token, response=response,
                                             session=session)

    if not current_user.is_owner:
        raise ERROR_403_FORBIDDEN

    user_for_revoke = await _get_user(user_id=user_id, session=session)

    if not user_for_revoke.is_admin:
        raise ERROR_409_CONFLICT

    if user_for_revoke is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id!r} not found")

    updated_user_params = {
        "roles": user_for_revoke.revoke_admin_role()
    }

    try:
        updated_user_id = await _update_user(user_id=user_id, updated_params=updated_user_params, session=session)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Error on database side')
    return UserID(user_id=updated_user_id)
