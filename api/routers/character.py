from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import character as character_models
from api.utils import auth as auth_utils, in_array

router = APIRouter(prefix="/characters")

@router.get(path='/')
def get(
        db: Session = Depends(get_db),
):
    return db.query(character_models.Character).all()

@router.get(path='/{id}')
def get_by_character(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        id: int,
        db: Session = Depends(get_db),
):
    data = db.query(character_models.RequestCharacter) \
        .filter_by(character_id=id) \
        .all()

    for d in data:
        for idx, e in enumerate(d.data):
            status_found = db.query(character_models.RequestCharacterUser) \
                .filter_by(request_character_id=d.id) \
                .filter_by(user_id=user_id) \
                .filter_by(ref_data=str(idx)) \
                .first()

            if status_found:
                e['status'] = status_found.status

    return data

@router.put(path='/reset')
def reset(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
):
    character = character_models.RequestCharacter()
    character.reset(db, user_id)
    return "OK"

@router.put(path='/{character_id}/{box_id}')
@router.put(path='/{character_id}/{box_id}/')
def update_status(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        character_id: int,
        box_id: int,
        answer: str,
        db: Session = Depends(get_db),
):
    data = db.query(character_models.RequestCharacter) \
        .filter_by(character_id=character_id) \
        .filter_by(box_id=box_id) \
        .first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requête de personnage invalide."
        )

    found = None
    found_data = None
    for idx, d in enumerate(data.data):
        if answer == ",".join(d['ask']):
            found = idx
            found_data = d

    if found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pas de réponse trouvée dans character_request"
        )

    exists = db.query(character_models.RequestCharacterUser) \
        .filter_by(request_character_id=data.id) \
        .filter_by(user_id=user_id) \
        .filter_by(ref_data=str(found)) \
        .first()

    if not exists:
        new = character_models.RequestCharacterUser(
            user_id=user_id,
            request_character_id=data.id,
            ref_data=found,
            status=True
        )
        db.add(new)
    else:
        exists.status = True

    db.commit()
    return found_data