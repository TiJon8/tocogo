from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from db import TaskLevel, ActiveObject


class NewTask(BaseModel):
    task_description: str
    task_level: TaskLevel
    composite_id: UUID | None = None


class ShowTask(NewTask):
    task_id: UUID
    user_id: UUID | None = None
    created_at: datetime
    task_status: ActiveObject
    closed_at: datetime | None = None


class PatchTask(BaseModel):
    task_description: str | None = None
    task_level: TaskLevel | None = None
