from typing import List, Optional

import genotype_api.models
from genotype_api.models import users, models
from sqlalchemy.orm import Session


def get_user(db: Session, user_id: int):
    return db.query(genotype_api.models.User).filter(genotype_api.models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[genotype_api.models.User]:
    return (
        db.query(genotype_api.models.User).filter(genotype_api.models.User.email == email).first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[genotype_api.models.User]:
    return db.query(genotype_api.models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: genotype_api.models.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = genotype_api.models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
