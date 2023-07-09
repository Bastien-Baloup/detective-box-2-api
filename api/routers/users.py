from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import users as user_models
from api.schemas import auth as auth_schemas
from api.schemas import users as user_schemas
from api.utils import auth as auth_utils

router = APIRouter(prefix="/users")


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
            detail="user_exists"
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
            detail="user_not_found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not auth_utils.verify_password(user.password, exists.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password_error",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": auth_utils.create_access_token({"id": exists.id}),
        "token_type": "bearer",
    }
