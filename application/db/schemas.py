from typing import TYPE_CHECKING

import uuid
from operator import attrgetter
from datetime import datetime, timezone

from sqlalchemy import String, Column, Text, MetaData, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.engine.default import DefaultExecutionContext
from sqlalchemy.sql import func
from enum import Enum
from db_config import sqlalchemy_config


class PortalRoles(str, Enum):
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"
    ROLE_PORTAL_OWNER = "ROLE_PORTAL_OWNER"


class ActiveObject(str, Enum):
    active = "active"
    done = "done"


class TaskLevel(str, Enum):
    free = "free"
    optimal = "optimal"
    urgent = "urgent"


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type or MSSQL's UNIQUEIDENTIFIER,
    otherwise uses CHAR(32), storing as stringified hex values.

    """

    impl = CHAR
    cache_ok = True

    _default_type = CHAR(32)
    _uuid_as_str = attrgetter("hex")

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(self._default_type)

    def process_bind_param(self, value, dialect):
        if value is None or dialect.name in ("postgresql", "mssql"):
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return self._uuid_as_str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class GUIDHyphens(GUID):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type or MSSQL's UNIQUEIDENTIFIER,
    otherwise uses CHAR(36), storing as stringified uuid values.

    """

    _default_type = CHAR(36)
    _uuid_as_str = str


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=sqlalchemy_config.naming_conventions)

    type_annotation_map = {
        uuid.UUID: GUID,
    }


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str | None] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))
    phone_number: Mapped[str]
    email: Mapped[str | None] = mapped_column(nullable=True, unique=True)
    roles = Column(ARRAY(String), nullable=True)
    is_active: Mapped[bool]
    # roles: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    composites: Mapped[list["Composite"]] = relationship(back_populates="user", lazy="selectin")
    tasks: Mapped[list["Task"]] = relationship(back_populates="user", lazy="selectin")

    @property
    def is_owner(self):
        return PortalRoles.ROLE_PORTAL_OWNER in self.roles

    @property
    def is_admin(self):
        return PortalRoles.ROLE_PORTAL_ADMIN in self.roles

    def enrich_admin_role(self):
        if not self.is_admin:
            return {*self.roles, PortalRoles.ROLE_PORTAL_ADMIN}

    def revoke_admin_role(self):
        if self.is_admin:
            return {role for role in self.roles if role != PortalRoles.ROLE_PORTAL_ADMIN}


# print(CreateTable(User.__table__).compile(dialect=postgresql.dialect()))


class AuthUser(Base):
    __tablename__ = "auth_users"

    auth_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    identity_number: Mapped[int] = mapped_column(nullable=False)


class Composite(Base):
    __tablename__ = "composites"

    @staticmethod
    def get_time():
        return datetime.now(timezone.utc).replace(microsecond=0)

    composite_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    composite_name: Mapped[str] = mapped_column(nullable=False)
    composite_description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=get_time)
    composite_status: Mapped[ActiveObject]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(column="users.user_id"))

    user: Mapped["User"] = relationship(back_populates="composites", lazy="selectin")
    tasks: Mapped[list["Task"]] = relationship(back_populates='composite', lazy="selectin")


class Task(Base):
    __tablename__ = 'tasks'

    @staticmethod
    def get_time():
        return datetime.now(timezone.utc).replace(microsecond=0)

    @staticmethod
    def close_task(context: DefaultExecutionContext):
        try:
            if context.get_current_parameters()["task_status"]:
                return datetime.now(timezone.utc).replace(microsecond=0)
        except KeyError:
            return None

    task_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    task_level: Mapped[TaskLevel]
    composite_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(column="composites.composite_id"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(column="users.user_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=get_time)
    task_status: Mapped[ActiveObject]
    closed_at: Mapped[datetime] = mapped_column(nullable=True, onupdate=close_task)

    composite: Mapped["Composite"] = relationship(back_populates="tasks", lazy="selectin")
    user: Mapped["User"] = relationship(back_populates="tasks", lazy="selectin")



