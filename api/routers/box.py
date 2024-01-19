from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import box as box_models
from api.schemas import box as box_schemas
from api.utils import auth as auth_utils
from api.enums import BoxStatus

from api.schemas.box import Box

router = APIRouter(prefix="/box")


@router.get(path='/')
def get(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
):
    box = db.query(box_models.Box).all()
    for b in box:
        b_user = db.query(box_models.UserBox) \
            .filter_by(user_id=user_id) \
            .filter_by(box_id=b.id) \
            .first()

        if b_user:
            b.status = b_user.status

    return box


@router.put(path='/reset')
def reset(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
):
    box = box_models.UserBox()
    box.reset(db, user_id)
    return 'Reset successful'

@router.put(path='/{id}/')
@router.put(path='/{id}')
def update_status(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        id: int,
        status: box_schemas.BoxStatus,
        db: Session = Depends(get_db),
):
    box_exists = db.query(box_models.Box).filter_by(id=id).first()

    if not box_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Box not found"
        )

    status_exists = db.query(box_models.UserBox) \
        .filter_by(box_id=id) \
        .filter_by(user_id=user_id) \
        .first()

    if not status_exists:
        new = box_models.UserBox(
            box_id=id,
            user_id=user_id,
            status=status.status
        )
        db.add(new)
    else:
        status_exists.status = status.status

    db.commit()
    return 'OK'
