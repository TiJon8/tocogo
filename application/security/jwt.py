import uuid
from uuid import UUID

from datetime import timedelta, datetime, timezone
from typing import Optional

from jose import jwt

from .jwt_config import jwt_config


def encode_jwt(data: dict,
               expire_minutes: int = jwt_config.ACCESS_TOKEN_EXPIRE,
               expire_timedelta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = datetime.now(timezone.utc) + expire_timedelta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire, iat=now, jti=str(uuid.uuid4()))
    encoded_jwt = jwt.encode(claims=to_encode, key=jwt_config.SECRET_KEY, algorithm=jwt_config.ALGORITHM)
    return encoded_jwt


def create_jwt(token_type: str,
               jwt_data: dict,
               expire_minutes: int = jwt_config.ACCESS_TOKEN_EXPIRE,
               expire_timedelta: timedelta | None = None) -> str:

    jwt_payload = {jwt_config.type.TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(jwt_data)
    return encode_jwt(data=jwt_payload,
                      expire_minutes=expire_minutes,
                      expire_timedelta=expire_timedelta)


def create_access_token(user_id: UUID) -> str:
    jwt_payload = {
        "sub": str(user_id)
    }
    return create_jwt(token_type=jwt_config.type.ACCESS_TOKEN_TYPE, jwt_data=jwt_payload,
                      expire_minutes=jwt_config.ACCESS_TOKEN_EXPIRE)


def create_refresh_token(user_id: UUID) -> str:
    jwt_payload = {
        "sub": str(user_id)
    }
    return create_jwt(token_type=jwt_config.type.REFRESH_TOKEN_TYPE, jwt_data=jwt_payload,
                      expire_timedelta=timedelta(days=jwt_config.REFRESH_TOKEN_EXPIRE))
