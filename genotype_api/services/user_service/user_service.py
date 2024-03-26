"""Module to holds the plate service."""

from fastapi import HTTPException
from pydantic import EmailStr

from sqlmodel import Session
from starlette import status

from genotype_api.database.crud.create import create_user
from genotype_api.database.crud.delete import delete_user
from genotype_api.database.crud.read import (
    get_user_by_id,
    get_users_with_skip_and_limit,
    get_user_by_email,
)
from genotype_api.database.crud.update import update_user_email
from genotype_api.database.models import User, Plate
from genotype_api.dto.plate import PlateResponse
from genotype_api.dto.user import UserResponse, UserRequest


class UserService:

    def __init__(self, session: Session):
        self.session: Session = session

    @staticmethod
    def _get_plates_on_user(user: User) -> list[PlateResponse]:
        plates_response: list[PlateResponse] = []
        for plate in user.plates:
            if plate:
                plate_response = PlateResponse(
                    created_at=plate.created_at,
                    plate_id=plate.plate_id,
                    id=plate.id,
                    signed_by=plate.signed_by,
                    signed_at=plate.signed_at,
                )
                plates_response.append(plate_response)
        return plates_response if plates_response else None

    def _get_user_response(self, user: User) -> UserResponse:
        plates: list[PlateResponse] = self._get_plates_on_user(user)
        return UserResponse(email=user.email, name=user.name, id=user.id, plates=plates)

    def create_user(self, user: UserRequest):
        existing_user: User = get_user_by_email(session=self.session, email=user.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already registered.")
        new_user: User = create_user(session=self.session, user=user)
        return self._get_user_response(new_user)

    def read_users(self, skip: int, limit: int) -> list[UserResponse]:
        users: list[User] = get_users_with_skip_and_limit(
            session=self.session, skip=skip, limit=limit
        )
        return [self._get_user_response(user) for user in users]

    def read_user(self, user_id: int) -> UserResponse:
        user: User = get_user_by_id(session=self.session, user_id=user_id)
        return self._get_user_response(user)

    def delete_user(self, user_id: int):
        user: User = get_user_by_id(session=self.session, user_id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.plates:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="User previously signed plates, please archive instead",
            )
        delete_user(session=self.session, user=user)

    def update_user_email(self, user_id: int, email: EmailStr):
        user: User = get_user_by_id(session=self.session, user_id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user: User = update_user_email(session=self.session, user=user, email=email)
        return self._get_user_response(user)
