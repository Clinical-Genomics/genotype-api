from typing import List, Optional

from genotype_api.models import User, UserCreate
from sqlmodel import select, Session
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


def get_user(session: Session, user_id: int):
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).one()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_users(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_user(db: Session, user: UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
