from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from db import ActiveObject
from .tasks import ShowTask


class NewComposite(BaseModel):
    composite_name: str
    composite_description: str | None = None


class CompositeID(BaseModel):
    composite_id: UUID


class ShowComposite(NewComposite, CompositeID):
    created_at: datetime
    composite_status: ActiveObject
    user_id: UUID
    tasks: list["ShowTask"] | list[None] = None


class PatchComposite(BaseModel):
    composite_name: str | None = None
    composite_description: str | None = None

