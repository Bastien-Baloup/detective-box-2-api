from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from password_generator import PasswordGenerator
from mailjet_rest import Client

from api.database import get_db
from api.models import users as user_models
from api.schemas import auth as auth_schemas
from api.schemas import users as user_schemas
from api.utils import auth as auth_utils
from api.utils.mail import Mail
from api.config import settings
import datetime

router = APIRouter(prefix="/users")


@router.put('/end_box/{id}')
def update_end_box1(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        id: int,
        db: Session = Depends(get_db),
):
    user = db.query(user_models.User)\
        .filter_by(id=user_id)\
        .first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if id == 1:
        user.end_box1 = datetime.datetime.now()
    if id == 2:
        user.end_box2 = datetime.datetime.now()
    if id == 3:
        user.end_box3 = datetime.datetime.now()

    db.commit()

    return 'OK'

@router.put(
    path="/password",
    response_model=user_schemas.User
)
def update(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        user: user_schemas.UserUpdatePass,
        db: Session = Depends(get_db),
):
    try:
        exists = db \
            .query(user_models.User) \
            .filter_by(id=user_id) \
            .first()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compte non trouvé"
            )

        exists.password = auth_utils.get_password_hash(user.password)
        db.commit()

        return exists
    except HTTPException as e:
        raise e


@router.put(
    path="/{id}",
    response_model=user_schemas.User
)
def update_user(
        id: int,
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        user: user_schemas.UserUpdate,
        db: Session = Depends(get_db),
):
    try:
        exists = db \
            .query(user_models.User) \
            .filter_by(id=id) \
            .first()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compte non trouvé"
            )

        exists.name = user.name
        exists.email = user.email
        db.commit()

        return exists
    except HTTPException as e:
        raise e


@router.get(
    path="/me",
    response_model=user_schemas.User
)
def me(
        user_id: Annotated[int, Depends(auth_utils.get_connected_user_id)],
        db: Session = Depends(get_db),
):
    try:
        return db.query(user_models.User).filter_by(id=user_id).first()
    except HTTPException as e:
        raise e


@router.post(
    path="/",
    response_model=user_schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Create user"
)
def create(
        user: user_schemas.UserCreate,
        db: Session = Depends(get_db)
):
    """Create a new user"""
    exists = db \
        .query(user_models.User) \
        .filter_by(email=user.email) \
        .first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte éxiste déjà pour cette adresse email."
        )
    db_user = user_models.User(
        email=user.email,
        password=auth_utils.get_password_hash(user.password),
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post(
    path="/login",
    summary="Login user",
    response_model=auth_schemas.Token
)
def login(
        user: user_schemas.UserBase,
        db: Session = Depends(get_db)
):
    exists: user_schemas.User = (
        db.query(user_models.User).filter_by(email=user.email).first()
    )

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not auth_utils.verify_password(user.password, exists.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": auth_utils.create_access_token({"id": exists.id}),
        "token_type": "bearer",
    }


@router.post(
    path="/forgot_password",
    summary="Forgot Password",
    response_model=str
)
def password_forgot(
        email: user_schemas.UserForgotPassword,
        db: Session = Depends(get_db)
):
    exists: user_schemas.User = (
        db.query(user_models.User).filter_by(email=email.email).first()
    )

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )

    pwo = PasswordGenerator()
    temp_password = pwo.generate()
    exists.password = auth_utils.get_password_hash(temp_password)

    mail = Mail()
    receiver = exists.email
    mail.send(
        receiver=receiver,
        message=mail.mail_password_forgot(receiver, temp_password)
    )

    db.commit()

    return 'OK'

