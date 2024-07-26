import random
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .models import CreateUser, ResponseSignUp, VerifySignUp
from db import User, DALUser, PortalRoles, DALAuth, DALTask, Composite, TaskLevel
from extentions import (ERROR_404_USER_NOT_FOUND,
                        ERROR_404_PAIR_NOT_FOUND,
                        ERROR_422_UNPROCESSABLE_ENTITY,
                        ERROR_404_COMPOSITE_NOT_FOUND)
from security import create_access_token, create_refresh_token


""" USER helpers """


async def _delete_user(user_id: UUID, session: AsyncSession):
    async with session.begin():
        user_dal = DALUser(session)
        deleted_user_id = await user_dal.delete_user(user_id)
        if deleted_user_id is None:
            raise ERROR_404_USER_NOT_FOUND.detail.format(id=user_id)
        return deleted_user_id


async def _get_user(user_id: UUID, session: AsyncSession):
    async with session.begin():
        user_dal = DALUser(session)
        user = await user_dal.get_user(user_id)
        if user is None:
            raise ERROR_404_USER_NOT_FOUND.detail.format(id=user_id)
        return user


async def _update_user(user_id: UUID, updated_params: dict, session: AsyncSession) -> User.user_id:
    async with session.begin():
        user_dal = DALUser(session)
        update_user_id = await user_dal.update_user(user_id, **updated_params)
        return update_user_id.user_id


""" AUTH helpers """


async def _add_new_user(phone_number: str, first_name: str, last_name: str, session: AsyncSession) -> User:
    user_dal = DALUser(session)
    return await user_dal.create_user(phone_number=phone_number, first_name=first_name, last_name=last_name,
                                      roles=[PortalRoles.ROLE_PORTAL_USER,])


async def _sign_up(body: CreateUser, session: AsyncSession) -> ResponseSignUp:
    async with session.begin():
        identity_number = random.randint(10_000, 99_999)
        auth_dal = DALAuth(session)
        pair_id = await auth_dal.add_new_pair(phone_number=body.phone_number,
                                              first_name=body.first_name,
                                              last_name=body.last_name,
                                              identity_number=identity_number)
        return ResponseSignUp(pair_id=pair_id)


async def _verify_identity_number(body: VerifySignUp, session: AsyncSession) -> tuple[str, str]:
    async with session.begin():
        auth_dal = DALAuth(session)
        check_pair = await auth_dal.get_identity_number(pair_id=body.pair_id)
        if check_pair is None:
            raise ERROR_404_PAIR_NOT_FOUND
        if check_pair.identity_number != body.identity_number:
            raise ERROR_422_UNPROCESSABLE_ENTITY

        user = await _add_new_user(phone_number=check_pair.phone_number, first_name=check_pair.first_name,
                                   last_name=check_pair.last_name,
                                   session=session)
        access_token = create_access_token(user_id=user.user_id)
        refresh_token = create_refresh_token(user_id=user.user_id)
        return access_token, refresh_token


""" COMPOSITES & TASKS """


async def _create_composite(composite_name: str, composite_description: str,
                            for_user_id: UUID, session: AsyncSession) -> Composite:
    async with session.begin():
        composite_dal = DALTask(db_session=session)
        return await composite_dal.create_composite(composite_name=composite_name,
                                                    composite_description=composite_description,
                                                    for_user_id=for_user_id)


async def _get_composite(composite_id: UUID, session: AsyncSession):
    async with session.begin():
        composite_dal = DALTask(db_session=session)
        composite = await composite_dal.get_composite(composite_id=composite_id)
        if composite is None:
            raise ERROR_404_COMPOSITE_NOT_FOUND.detail.format(id=composite_id)
        return composite


async def _delete_composite(composite_id: UUID, session: AsyncSession):
    async with session.begin():
        composite_dal = DALTask(db_session=session)
        return await composite_dal.delete_composite(composite_id=composite_id)


async def _close_composite(composite_id: UUID, session: AsyncSession):
    async with session.begin():
        composite_dal = DALTask(db_session=session)
        return await composite_dal.close_composite(composite_id=composite_id)


async def _update_composite(composite_id: UUID, updated_params: dict, session: AsyncSession) -> Composite:
    async with session.begin():
        composite_dal = DALTask(db_session=session)
        updated_composite = await composite_dal.update_composites(composite_id=composite_id, **updated_params)
        return updated_composite


async def _create_task(task_description: str,
                       task_level: TaskLevel,
                       composite_id: UUID | None,
                       user_id: str | None,
                       session: AsyncSession):
    async with session.begin():
        task_dal = DALTask(db_session=session)
        return await task_dal.create_task(task_description=task_description,
                                          user_id=user_id,
                                          task_level=task_level,
                                          composite_id=composite_id)


async def _get_task(composite_id: UUID | None, user_id: UUID | None, session: AsyncSession):
    async with session.begin():
        task_dal = DALTask(db_session=session)
        return await task_dal.get_task(composite_id=composite_id, user_id=user_id)


async def _delete_task(task_id: UUID, session: AsyncSession, composite_id: UUID | None = None,
                       user_id: UUID | None = None):
    async with session.begin():
        task_dal = DALTask(db_session=session)
        return await task_dal.delete_task(task_id, composite_id, user_id)


async def _update_task(task_id: UUID, updated_params: dict, session: AsyncSession, composite_id: UUID | None = None,
                       user_id: UUID | None = None):
    async with session.begin():
        task_dal = DALTask(db_session=session)
        return await task_dal.update_task(task_id, composite_id=composite_id, user_id=user_id, **updated_params)


async def _close_task(task_id: UUID, session: AsyncSession, composite_id: UUID | None = None,
                      user_id: UUID | None = None):
    async with session.begin():
        task_dal = DALTask(db_session=session)
        return await task_dal.close_task(task_id, composite_id=composite_id, user_id=user_id)
