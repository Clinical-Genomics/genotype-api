"""Routes for users"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar
from starlette import status
from starlette.responses import JSONResponse

from genotype_api.database.crud.read import (
    get_user,
    get_user_by_email,
    get_users_with_skip_and_limit,
)
from genotype_api.database.crud.update import update_user_email
from genotype_api.database.crud import delete, create
from genotype_api.database.models import User
from genotype_api.dto.dto import UserRead, UserCreate, UserReadWithPlates
from genotype_api.database.session_handler import get_session
from genotype_api.security import get_active_user

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


router = APIRouter()


@router.get("/{user_id}", response_model=UserReadWithPlates)
def read_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> User:
    return get_user(session=session, user_id=user_id)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> JSONResponse:
    user: User = get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.plates:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User previously signed plates, please archive instead",
        )
    delete.delete_user(session=session, user=user)
    return JSONResponse(content="User deleted successfully", status_code=status.HTTP_200_OK)


@router.put("/{user_id}/email", response_model=User)
def change_user_email(
    user_id: int,
    email: EmailStr,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> User:
    user: User = get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user: User = update_user_email(session=session, user=user, email=email)
    return user


@router.get("/", response_model=list[UserRead])
def read_users(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> list[User]:
    return get_users_with_skip_and_limit(session=session, skip=skip, limit=limit)


@router.post("/", response_model=User)
def create_user(
    user: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    existing_user: User = get_user_by_email(session=session, email=user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user: User = create.create_user(session=session, user=user)
    return new_user
