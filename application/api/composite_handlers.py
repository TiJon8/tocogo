from uuid import UUID

from fastapi import APIRouter, Request, Response, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from .models import NewComposite, ShowComposite, PatchComposite, ShowTask, CompositeID
from .actions import check_cookies
from .crud import _create_composite, _update_composite, _get_composite, _delete_composite, _close_composite
from db import db_helper


router = APIRouter()


@router.post('/', response_model=ShowComposite, response_model_exclude_none=True,
             status_code=status.HTTP_201_CREATED)
async def create_composite(body: NewComposite,
                           request: Request,
                           response: Response,
                           session: AsyncSession = Depends(db_helper.session_getter)):

    current_user = await check_cookies(request=request, response=response, session=session)

    new_composite = await _create_composite(composite_name=body.composite_name,
                                            composite_description=body.composite_description,
                                            for_user_id=current_user.user_id,
                                            session=session)

    return ShowComposite(composite_id=new_composite.composite_id,
                         composite_name=new_composite.composite_name,
                         composite_description=new_composite.composite_description,
                         created_at=new_composite.created_at,
                         composite_status=new_composite.composite_status,
                         user_id=new_composite.user_id)


@router.get('/', response_model=ShowComposite)
async def get_composite(composite_id: UUID,
                        request: Request,
                        response: Response,
                        session: AsyncSession = Depends(db_helper.session_getter)):

    await check_cookies(request=request, response=response, session=session)
    composite = await _get_composite(composite_id=composite_id, session=session)
    tasks = [ShowTask.model_validate(row, from_attributes=True) for row in composite.tasks]

    return ShowComposite(composite_id=composite.composite_id,
                         composite_name=composite.composite_name,
                         composite_description=composite.composite_description,
                         created_at=composite.created_at,
                         composite_status=composite.composite_status,
                         user_id=composite.user_id,
                         tasks=tasks)


@router.delete('/', response_model=CompositeID)
async def delete_composite(composite_id: UUID,
                           request: Request,
                           response: Response,
                           session: AsyncSession = Depends(db_helper.session_getter)):

    await check_cookies(request=request, response=response, session=session)
    composite = await _delete_composite(composite_id=composite_id, session=session)

    return CompositeID(composite_id=composite.composite_id)


@router.patch('/', response_model=ShowComposite)
async def patch_composite(composite_id: UUID,
                          body: PatchComposite,
                          request: Request,
                          response: Response,
                          session: AsyncSession = Depends(db_helper.session_getter)):

    await check_cookies(request=request, response=response, session=session)

    updated_params = body.dict(exclude_none=True)

    updated_composite = await _update_composite(composite_id=composite_id, updated_params=updated_params,
                                                session=session)
    tasks = [ShowTask.model_validate(row, from_attributes=True) for row in updated_composite.tasks]

    return ShowComposite(composite_id=updated_composite.composite_id,
                         composite_name=updated_composite.composite_name,
                         composite_description=updated_composite.composite_description,
                         created_at=updated_composite.created_at,
                         composite_status=updated_composite.composite_status,
                         user_id=updated_composite.user_id,
                         tasks=tasks)


@router.post('/close', response_model=ShowComposite)
async def close_composite(composite_id: UUID,
                          request: Request,
                          response: Response,
                          session: AsyncSession = Depends(db_helper.session_getter)):

    await check_cookies(request=request, response=response, session=session)
    composite = await _close_composite(composite_id=composite_id, session=session)
    tasks = [ShowTask.model_validate(row, from_attributes=True) for row in composite.tasks]

    return ShowComposite(composite_id=composite.composite_id,
                         composite_name=composite.composite_name,
                         composite_description=composite.composite_description,
                         created_at=composite.created_at,
                         composite_status=composite.composite_status,
                         user_id=composite.user_id,
                         tasks=tasks)
