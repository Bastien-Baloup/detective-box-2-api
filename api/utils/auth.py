from typing import Annotated

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status
from api.config import settings
from fastapi.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED


class OAuth2PasswordQuery:
    def __call__(self, request: Request):
        token = request.query_params.get('token')
        if not token:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token


pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_password = OAuth2PasswordBearer(tokenUrl="token")
oauth2_query = OAuth2PasswordQuery()


def verify_password(password: str, hash: str):
    return pwd_context.verify(password, hash)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(weeks=2)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, algorithm="HS256", key=settings.secret_key)


def get_connected_user_id(token: Annotated[str, Depends(oauth2_password)]):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Connexion expirée",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            key=settings.secret_key,
            algorithms=["HS256"]
        )
    except JWTError:
        raise credential_exception

    user_id = payload.get("id")
    if not user_id:
        raise credential_exception
    return user_id


def is_connected_admin(
        key: Annotated[str, Depends(oauth2_password)]
):
    if settings.admin_token != key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="super_admin_operation"
        )

    return True


def is_connected_admin_query(
        token: Annotated[str, Depends(oauth2_query)]
):
    if settings.admin_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="super_admin_operation"
        )

    return True
