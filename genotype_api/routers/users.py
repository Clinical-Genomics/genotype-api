"""Routes for users"""

from typing import List

import genotype_api.crud.users
from fastapi import APIRouter, Depends, HTTPException
from genotype_api import crud
from genotype_api.database import get_db
from genotype_api.schemas.users import User, UserCreate
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = genotype_api.crud.users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = genotype_api.crud.users.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return genotype_api.crud.users.create_user(db=db, user=user)


@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    users = genotype_api.crud.users.get_users(db, skip=skip, limit=limit)
    return users
