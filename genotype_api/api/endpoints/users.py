"""Routes for users"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr
from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse

from genotype_api.database.crud.read import (
    get_user_by_id,
    get_user_by_email,
    get_users_with_skip_and_limit,
)
from genotype_api.database.crud.update import update_user_email
from genotype_api.database.crud import delete, create
from genotype_api.database.models import User
from genotype_api.dto.dto import UserRead, UserReadWithPlates
from genotype_api.database.session_handler import get_session
from genotype_api.dto.user import UserRequest, UserResponse
from genotype_api.security import get_active_user
from genotype_api.services.user_service.user_service import UserService

router = APIRouter()


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(session)


@router.get("/{user_id}", response_model=UserReadWithPlates)
def read_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_active_user),
) -> UserResponse:
    return user_service.read_user(user_id)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_active_user),
) -> JSONResponse:
    return user_service.delete_user(user_id)


@router.put("/{user_id}/email", response_model=User)
def change_user_email(
    user_id: int,
    email: EmailStr,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_active_user),
) -> User:
    return user_service.update_user_email(user_id=user_id, email=email)


@router.get("/", response_model=list[UserRead])
def read_users(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_active_user),
) -> list[UserResponse]:
    return user_service.read_users(skip=skip, limit=limit)


@router.post("/", response_model=User)
def create_user(
    user: UserRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_active_user),
):
    return user_service.create_user(user)
