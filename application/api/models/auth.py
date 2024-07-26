from uuid import UUID

from pydantic import BaseModel


class ResponseSignUp(BaseModel):
    pair_id: UUID


class VerifySignUp(ResponseSignUp):
    identity_number: int


class ResponseToken(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class ExpiredTokenSignature(BaseModel):
    detail: str = "expired token signature"