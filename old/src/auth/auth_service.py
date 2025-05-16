from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from db.manager import Database
from schema.schema import Specialists
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from typing import Annotated
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError
from main import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
import jwt


class AuthUser(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class TokenData(BaseModel):
    email: str | None = None


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


def token_decode(token: Annotated[str, Depends(JWTBearer())]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    return token_data


class AuthService:
    @staticmethod
    async def get_current_user(
        token: Annotated[str, Depends(JWTBearer())],
        session: Session = Depends(Database.get_session),
    ):
        token_data = token_decode(token)
        statement = select(Specialists).where(Specialists.email == token_data.email)
        user = session.exec(statement).first()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def create_access_token(email: str):
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub": email}

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
