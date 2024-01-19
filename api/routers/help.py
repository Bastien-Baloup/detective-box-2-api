from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import help as help_models
from api.schemas.help import Help, Status
from api.utils import auth as auth_utils
from api.utils import in_array
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter(prefix="/help")


@router.get(path='/')
def get(
        # user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
) -> List[Help]:
    return db.query(help_models.Help).all()


@router.get(path='/{box_id}')
def get_by_box(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        box_id: int,
        db: Session = Depends(get_db),
):
    help = db \
        .query(help_models.Help) \
        .filter_by(box_id=box_id) \
        .first()

    for d in help.data:
        exists = db\
            .query(help_models.HelpUser)\
            .filter_by(help_id=help.id)\
            .filter_by(user_id=user_id)\
            .filter_by(ref_data=d['id'])\
            .first()

        if exists:
            d['status'] = exists.status

    return help


@router.put(path='/reset')
def reset(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
) -> str:
    help = help_models.HelpUser()
    help.reset(db, user_id)

    return 'OK'


@router.put(path='/{box_id}')
@router.put(path='/{box_id}/')
def update_status(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        box_id: int,
        id: str,
        new_status: Status,
        db: Session = Depends(get_db),
):
    data = db.query(help_models.Help) \
        .filter_by(box_id=box_id) \
        .first()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requête de renfort invalide.")

    found = None
    for idx, d in enumerate(data.data):
        if d['id'] == id:
            found = idx

    if found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id non trouvé dans la table help.")

    exists = db.query(help_models.HelpUser) \
        .filter_by(help_id=data.id) \
        .filter_by(user_id=user_id) \
        .filter_by(ref_data=str(id)) \
        .first()

    if not exists:
        new = help_models.HelpUser(
            user_id=user_id,
            help_id=data.id,
            ref_data=id,
            status=new_status.status
        )
        db.add(new)
    else:
        exists.status = new_status.status

    db.commit()
    return 'OK'
