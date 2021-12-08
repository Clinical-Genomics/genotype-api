"""Routes for users"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from genotype_api.database import get_session
from genotype_api.schemas.users import User, UserCreate
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound

router = APIRouter()


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, session: Session = Depends(get_session)) -> User:
    try:
        user: User = session.exec(select(User).where(User.id == user_id)).one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=List[User])
def read_users(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
) -> List[User]:
    users: List[User] = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.post("/", response_model=User)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    user: User = session.exec(select(User).where(User.email == user.email)).one()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    session.add(user)
    session.commit()
