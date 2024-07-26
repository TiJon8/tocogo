from uuid import UUID

from fastapi import APIRouter, Request, Response, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from .crud import _create_task, _get_task, _delete_task, _update_task, _close_task
from .actions import check_cookies
from .models import NewTask, ShowTask, PatchTask
from db import db_helper


router = APIRouter()


@router.post('/', response_model=ShowTask, status_code=status.HTTP_201_CREATED, response_model_exclude_none=True)
async def create_task(body: NewTask,
                      request: Request,
                      response: Response,
                      session: AsyncSession = Depends(db_helper.session_getter)) -> ShowTask:

    current_user = await check_cookies(request=request, response=response, session=session)
    task = await _create_task(body.task_description, body.task_level, body.composite_id, current_user.user_id, session)

    return ShowTask(task_id=task.task_id,
                    task_description=task.task_description,
                    task_level=task.task_level,
                    composite_id=task.composite_id,
                    user_id=task.user_id,
                    created_at=task.created_at,
                    task_status=task.task_status)


@router.get('/', response_model=ShowTask, response_model_exclude_none=True)
async def get_task(request: Request,
                   response: Response,
                   composite_id: UUID = None,
                   session: AsyncSession = Depends(db_helper.session_getter)):
    current_user = await check_cookies(request=request, response=response, session=session)
    task = await _get_task(composite_id=composite_id, user_id=current_user.user_id, session=session)

    return ShowTask.model_validate(task, from_attributes=True)


@router.delete('/')
async def delete_task(request: Request,
                      response: Response,
                      task_id: UUID,
                      composite_id: UUID = None,
                      session: AsyncSession = Depends(db_helper.session_getter)):

    current_user = await check_cookies(request=request, response=response, session=session)
    task = await _delete_task(task_id=task_id, session=session, composite_id=composite_id, user_id=current_user.user_id)
    return {"Task was deleted": task.task_id}


@router.patch("/", response_model=ShowTask, response_model_exclude_none=True)
async def patch_task(task_id: UUID,
                     body: PatchTask,
                     request: Request,
                     response: Response,
                     composite_id: UUID = None,
                     session: AsyncSession = Depends(db_helper.session_getter)):

    current_user = await check_cookies(request=request, response=response, session=session)
    updated_params = body.dict(exclude_none=True)
    task = await _update_task(task_id, updated_params, session, composite_id=composite_id, user_id=current_user.user_id)
    return ShowTask.model_validate(task, from_attributes=True)


@router.post("/close", response_model=ShowTask)
async def close_task(task_id: UUID,
                     request: Request,
                     response: Response,
                     composite_id: UUID = None,
                     session: AsyncSession = Depends(db_helper.session_getter)):

    current_user = await check_cookies(request=request, response=response, session=session)
    task = await _close_task(task_id, session, composite_id, current_user.user_id)

    return ShowTask.model_validate(task, from_attributes=True)
