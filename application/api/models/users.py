from typing import Optional
from uuid import UUID

from pydantic import BaseModel, constr

from . import ShowComposite, ShowTask


class UserID(BaseModel):
    user_id: UUID


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    phone_number: str


class ShowUser(CreateUser, UserID):
    email: str | None
    is_active: bool
    composites: list["ShowComposite"]
    tasks: list["ShowTask"]


class UpdateUserRequest(BaseModel):
    first_name: Optional[constr(min_length=1)] = None
    last_name: Optional[constr(min_length=1)] = None
    # убрать в дальнейшем возможность менять номер телефона
    phone_number: Optional[str] = None
    email: Optional[str] = None
