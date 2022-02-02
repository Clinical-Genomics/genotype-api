"""Routes for users"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from genotype_api.crud.users import get_user
from genotype_api.database import get_session
from genotype_api.models import User, UserRead, UserCreate, UserReadWithPlates
from sqlmodel import Session, select

from genotype_api.security import get_active_user

router = APIRouter()


@router.get("/{user_id}", response_model=UserReadWithPlates)
def read_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> User:
    return get_user(session=session, user_id=user_id)


@router.get("/", response_model=List[UserRead])
def read_users(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
) -> List[User]:
    users: List[User] = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.post("/", response_model=User)
def create_user(
    user: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    user_in_db: List[User] = session.exec(select(User).where(User.email == user.email)).all()
    if user_in_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
