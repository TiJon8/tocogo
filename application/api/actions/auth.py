from typing import Union

from fastapi import Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from application.db.dals import DALUser
from jose import ExpiredSignatureError
from application.db.schemas import User
from application.security import jwt_config, create_access_token
from extentions import ERROR_401_UNAUTHORIZED, ERROR_404_USER_NOT_FOUND
from ..models import ExpiredTokenSignature


async def _get_user(user_id: str, session: AsyncSession) -> User:
    async with session.begin():
        user_dal = DALUser(session)
        user = await user_dal.get_user(user_id=user_id)
        if user is None:
            raise ERROR_404_USER_NOT_FOUND
        return user


async def get_user_from_token(access_token: str, refresh_token: str, response: Response,
                              session: AsyncSession) -> Union[User, ExpiredTokenSignature]:
    try:
        payload = jwt.decode(token=access_token, key=jwt_config.SECRET_KEY, algorithms=[jwt_config.ALGORITHM])
        token_type = payload.get(jwt_config.type.TOKEN_TYPE_FIELD)
        if token_type != jwt_config.type.ACCESS_TOKEN_TYPE:
            raise ERROR_401_UNAUTHORIZED
        user_id = payload.get("sub")
        if user_id is None:
            raise ERROR_401_UNAUTHORIZED
        user = await _get_user(user_id=user_id, session=session)
        return user
    except ExpiredSignatureError:
        new_access_token = await encode_new_access_token(refresh_token=refresh_token, response=response,
                                                         session=session)
        response.set_cookie(key="xww-access-cookie", value=new_access_token, httponly=True)
        return await get_user_from_refresh_token(refresh_token=refresh_token, response=response, session=session)
    except JWTError:
        raise ERROR_401_UNAUTHORIZED


async def get_user_from_refresh_token(refresh_token: str,
                                      response: Response,
                                      session: AsyncSession) -> Union[User, ExpiredTokenSignature]:
    try:
        payload = jwt.decode(token=refresh_token, key=jwt_config.SECRET_KEY, algorithms=[jwt_config.ALGORITHM])
        user_id = payload.get("sub")
        user = await _get_user(user_id, session=session)
        return user
    except ExpiredSignatureError:
        response.delete_cookie(key="xww-access-cookie")
        response.delete_cookie(key="xws-security-cookie")
        return ExpiredTokenSignature()


async def encode_new_access_token(refresh_token: str, response: Response, session: AsyncSession) -> str:
    user = await get_user_from_refresh_token(refresh_token=refresh_token, response=response, session=session)
    return create_access_token(user_id=user.user_id)


async def check_cookies(request: Request, response: Response, session: AsyncSession):
    if not request.cookies.get("xww-access-cookie"):
        raise ERROR_401_UNAUTHORIZED
    access_token = request.cookies.get("xww-access-cookie")
    refresh_token = request.cookies.get("xws-security-cookie")
    current_user = await get_user_from_token(access_token=access_token, refresh_token=refresh_token, response=response,
                                             session=session)
    if isinstance(current_user, User):
        return current_user
    else:
        return ExpiredTokenSignature()
