import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from sse_starlette.sse import EventSourceResponse
from starlette.concurrency import run_in_threadpool

from api.utils.events import event_generator, create_client_queue

from api.database import get_db
from api.models import event as event_models
from api.schemas import event as event_schemas
from api.utils import auth as auth_utils

router = APIRouter(prefix="/events")

@router.get(path='/{box_id}')
def get_by_box_id(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        box_id: int,
        db: Session = Depends(get_db),
):
    event = db \
        .query(event_models.Event) \
        .filter_by(box_id=box_id) \
        .first()

    for d in event.data:
        exists = db \
            .query(event_models.EventUser) \
            .filter_by(event_id=event.id) \
            .filter_by(user_id=user_id) \
            .filter_by(ref_data=d['id']) \
            .first()

        if exists:
            d['status'] = exists.status

    return event


@router.put(path='/reset')
def reset(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
):
    event = event_models.EventUser()
    event.reset(db, user_id)

    return 'OK'


@router.put(path='/{box_id}')
@router.put(path='/{box_id}/')
def update_status(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        box_id: int,
        id: int,
        new_status: event_schemas.EventStatus,
        db: Session = Depends(get_db),
):
    data = db.query(event_models.Event) \
        .filter_by(box_id=box_id) \
        .first()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requête d'évènement invalide.")

    found = None
    for idx, d in enumerate(data.data):
        if d['id'] == id:
            found = idx

    if found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id non trouvé dans la table d'évènement.")

    exists = db.query(event_models.EventUser) \
        .filter_by(event_id=data.id) \
        .filter_by(user_id=user_id) \
        .filter_by(ref_data=str(id)) \
        .first()

    if not exists:
        new = event_models.EventUser(
            user_id=user_id,
            event_id=data.id,
            ref_data=id,
            status=new_status.status
        )
        db.add(new)
    else:
        exists.status = new_status.status

    db.commit()
    return 'OK'
