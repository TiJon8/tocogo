from typing import Any

from fastapi import APIRouter, Response, Request, Depends
from fastapi import HTTPException
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from .crud import _sign_up, _verify_identity_number
from .models import CreateUser, ResponseSignUp, VerifySignUp, ResponseToken
from application.db import db_helper
from application.security import create_access_token, create_refresh_token
from .actions.auth import encode_new_access_token

router = APIRouter()


@router.post('/registration', response_model=ResponseSignUp)
async def sign_up(body: CreateUser, session: AsyncSession = Depends(db_helper.session_getter)) -> ResponseSignUp:
    return await _sign_up(body, session=session)


@router.post('/registration/verify', status_code=status.HTTP_201_CREATED, response_model=ResponseToken)
async def verify_registration(body: VerifySignUp,
                              response: Response,
                              session: AsyncSession = Depends(db_helper.session_getter)) -> dict[str, str | Any]:
    access_token, refresh_token = await _verify_identity_number(body, session=session)
    response.set_cookie(key='xww-access-cookie', value=access_token, httponly=True)
    response.set_cookie(key='xws-security-cookie', value=refresh_token, httponly=True)
    return {"access_token": access_token, "refresh_token": refresh_token}


""" Test Points """


@router.post('/refresh', response_model=ResponseToken, response_model_exclude_none=True)
async def refresh_access_token(request: Request, response: Response,
                               session: AsyncSession = Depends(db_helper.session_getter)):
    if not request.cookies.get("xws-security-cookie"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    refresh_token = request.cookies.get("xws-security-cookie")
    access_token = await encode_new_access_token(refresh_token=refresh_token, session=session)
    response.set_cookie(key='xww-access-cookie', value=access_token, httponly=True)
    return {"access_token": access_token}


@router.post('/get-token', response_model=ResponseToken)
async def get_token(user_id, response: Response) -> dict[str, str | Any]:
    access_token = create_access_token(user_id=user_id)
    refresh_token = create_refresh_token(user_id=user_id)
    response.set_cookie(key='xww-access-cookie', value=access_token, httponly=True)
    response.set_cookie(key='xws-security-cookie', value=refresh_token, httponly=True)
    return {"access_token": access_token, "refresh_token": refresh_token}
