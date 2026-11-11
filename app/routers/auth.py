from fastapi import APIRouter, HTTPException, Response, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.deps import COOKIE_NAME, CurrentUser, SessionDep
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import Credentials, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


def set_auth_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(user_id),
        max_age=settings.jwt_expire_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: Credentials, response: Response, session: SessionDep) -> User:
    password_hash = await run_in_threadpool(hash_password, data.password)
    user = User(username=data.username, password_hash=password_hash)
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Користувач з таким іменем уже існує"
        ) from None
    set_auth_cookie(response, user.id)
    return user


@router.post("/login", response_model=UserRead)
async def login(data: Credentials, response: Response, session: SessionDep) -> User:
    user = await session.scalar(select(User).where(User.username == data.username))
    if user is None or not await run_in_threadpool(
        verify_password, data.password, user.password_hash
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неправильне ім'я або пароль")
    set_auth_cookie(response, user.id)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME)


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> User:
    return user
