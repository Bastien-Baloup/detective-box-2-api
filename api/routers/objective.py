from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import objective as objective_models
from api.schemas import objective as objective_schemas
from api.utils import auth as auth_utils

router = APIRouter(prefix="/objectives")


@router.get(path='/')
def get(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
):

    objectives = db.query(objective_models.Objective).all()

    for o in objectives:
        for d in o.data:
            exists = db\
                .query(objective_models.ObjectiveUser)\
                .filter_by(objective_id=o.id)\
                .filter_by(user_id=user_id)\
                .filter_by(ref_data=str(d['id']))\
                .first()

            if exists:
                d['status'] = exists.status

    return objectives


@router.put(path='/reset')
def reset(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
) -> str:
    data = db.query(objective_models.ObjectiveUser) \
        .filter_by(user_id=user_id) \
        .all()

    for d in data:
        db.delete(d)

    db.commit()

    return 'OK'


@router.put(path='/{box_id}')
def update_status(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        box_id: int,
        id: int,
        new_status: objective_schemas.ObjectiveStatus,
        db: Session = Depends(get_db),
):
    data = db.query(objective_models.Objective) \
        .filter_by(box_id=box_id) \
        .first()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    found = None
    for idx, d in enumerate(data.data):
        if d['id'] == id:
            found = idx

    if found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    exists = db.query(objective_models.ObjectiveUser) \
        .filter_by(objective_id=data.id) \
        .filter_by(user_id=user_id) \
        .filter_by(ref_data=str(id)) \
        .first()

    if not exists:
        new = objective_models.ObjectiveUser(
            user_id=user_id,
            objective_id=data.id,
            ref_data=id,
            status=new_status.status
        )
        db.add(new)
    else:
        exists.status = new_status.status

    db.commit()
    return 'OK'
