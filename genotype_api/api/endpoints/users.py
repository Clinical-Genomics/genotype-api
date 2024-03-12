"""Routes for users"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar
from starlette import status
from starlette.responses import JSONResponse

from genotype_api.database.crud.read import get_user
from genotype_api.database.models import (User, UserCreate, UserRead,
                                          UserReadWithPlates)
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
    session.delete(user)
    session.commit()
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
    user.email = email
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=list[UserRead])
def read_users(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> list[User]:
    users: list[User] = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.post("/", response_model=User)
def create_user(
    user: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    user_in_db: list[User] = session.exec(select(User).where(User.email == user.email)).all()
    if user_in_db:
        raise HTTPException(status_code=409, detail="Email already registered")
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
