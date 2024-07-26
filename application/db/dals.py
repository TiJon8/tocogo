from typing import Union
from uuid import UUID

from sqlalchemy import select, update, and_, Result, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import User, AuthUser, PortalRoles, Composite, Task, ActiveObject, TaskLevel


class DALUser:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_user(self, phone_number: str,
                          first_name: str,
                          last_name: str,
                          roles: list[PortalRoles]) -> User:

        new_user = User(phone_number=phone_number, first_name=first_name, last_name=last_name, is_active=True,
                        roles=roles)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[User, None]:
        stm = update(User).where(and_(User.user_id == user_id, User.is_active == True)).values(
            is_active=False).returning(User.user_id)
        res = await self.db_session.execute(stm)
        deleted_user_id_row = res.fetchone()
        return deleted_user_id_row[0]

    async def get_user(self, user_id: Union[str, UUID]) -> Union[User, None]:
        stm = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(stm)
        user_row = res.fetchone()
        return user_row[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Union[User, None]:
        stm = update(User).where(User.user_id == user_id).values(kwargs).returning(User)
        res = await self.db_session.execute(stm)
        update_user_row = res.fetchone()
        print(update_user_row)
        return update_user_row[0]


class DALAuth:

    def __init__(self, db_session):
        self.db_session = db_session

    async def add_new_pair(self, phone_number: str,
                           first_name: str,
                           last_name: str,
                           identity_number: int) -> AuthUser.auth_id:

        new_pair = AuthUser(phone_number=phone_number,
                            first_name=first_name,
                            last_name=last_name,
                            identity_number=identity_number)
        self.db_session.add(new_pair)
        await self.db_session.flush()
        return new_pair.auth_id

    async def get_identity_number(self, pair_id: UUID) -> AuthUser:
        stm = select(AuthUser).where(AuthUser.auth_id == pair_id)
        res = await self.db_session.execute(stm)
        auth_user_row = res.fetchone()
        return auth_user_row[0]


class DALTask:

    def __init__(self, db_session):
        self.db_session: AsyncSession = db_session

    async def create_composite(self, composite_name: str, composite_description: str, for_user_id: UUID) -> Composite:
        new_composite = Composite(composite_name=composite_name,
                                  composite_description=composite_description,
                                  composite_status=ActiveObject.active,
                                  user_id=for_user_id)
        self.db_session.add(new_composite)
        await self.db_session.flush()
        return new_composite

    async def get_composite(self, composite_id: UUID):
        stm = select(Composite).where(Composite.composite_id == composite_id)
        res = await self.db_session.execute(stm)
        composite = res.fetchone()
        return composite[0]

    async def delete_composite(self, composite_id: UUID):
        stm = delete(Composite).where(Composite.composite_id == composite_id).returning(Composite)
        res = await self.db_session.execute(stm)
        deleted_composite = res.fetchone()
        return deleted_composite[0]

    async def close_composite(self, composite_id: UUID):
        stm = (update(Composite)
               .where(and_(Composite.composite_id == composite_id,
                           Composite.composite_status == ActiveObject.active))
               .values(composite_status=ActiveObject.done)
               .returning(Composite))
        res = await self.db_session.execute(stm)
        closed_composite = res.fetchone()
        return closed_composite[0]

    async def update_composites(self, composite_id: UUID, **kwargs) -> Composite:
        stm = update(Composite).where(Composite.composite_id == composite_id).values(kwargs).returning(Composite)
        res: Result = await self.db_session.execute(stm)
        updated_composite = res.fetchone()
        return updated_composite[0]

    async def create_task(self,
                          task_description: str,
                          task_level: TaskLevel,
                          composite_id: UUID | None,
                          user_id: str | None) -> Task:
        if composite_id:
            task = Task(task_description=task_description,
                        task_level=task_level,
                        composite_id=composite_id,
                        task_status=ActiveObject.active)
        else:
            task = Task(task_description=task_description,
                        task_level=task_level,
                        user_id=user_id,
                        task_status=ActiveObject.active)
        self.db_session.add(task)
        await self.db_session.flush()
        return task

    async def get_task(self, composite_id: UUID | None = None, user_id: UUID | None = None):
        if composite_id:
            stm = select(Task).where(Task.composite_id == composite_id)
        else:
            stm = select(Task).where(Task.user_id == user_id)
        res = await self.db_session.execute(stm)
        composite = res.fetchone()
        return composite[0]

    async def delete_task(self, task_id: UUID, composite_id: UUID | None = None, user_id: UUID | None = None):
        if composite_id:
            stm = delete(Task).where(and_(Task.composite_id == composite_id, Task.task_id == task_id)).returning(Task)
        else:
            stm = delete(Task).where(and_(Task.user_id == user_id, Task.task_id == task_id)).returning(Task)
        res = await self.db_session.execute(stm)
        response = res.fetchone()
        return response[0]

    async def update_task(self, task_id: UUID, composite_id: UUID | None = None, user_id: UUID | None = None, **kwargs):
        if composite_id:
            stm = (update(Task).where(and_(Task.task_id == task_id, Task.composite_id == composite_id)).values(kwargs)
                   .returning(Task))
        else:
            stm = (update(Task).where(and_(Task.task_id == task_id, Task.user_id == user_id)).values(kwargs)
                   .returning(Task))
        res = await self.db_session.execute(stm)
        response = res.fetchone()
        return response[0]

    async def close_task(self, task_id: UUID, composite_id: UUID | None = None, user_id: UUID | None = None):
        if composite_id:
            stm = (update(Task)
                   .where(and_(Task.task_id == task_id,
                               Task.composite_id == composite_id,
                               Task.task_status == ActiveObject.active))
                   .values(task_status=ActiveObject.done).returning(Task))
        else:
            stm = (update(Task)
                   .where(and_(Task.task_id == task_id,
                               Task.user_id == user_id,
                               Task.task_status == ActiveObject.active))
                   .values(task_status=ActiveObject.done).returning(Task))
        res = await self.db_session.execute(stm)
        response = res.fetchone()
        return response[0]
