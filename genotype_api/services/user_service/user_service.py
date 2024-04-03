"""Module to holds the user service."""

from pydantic import EmailStr
from sqlmodel import Session
from genotype_api.database.crud.create import create_user
from genotype_api.database.crud.delete import delete_user
from genotype_api.database.crud.read import (
    get_user_by_id,
    get_users_with_skip_and_limit,
    get_user_by_email,
)
from genotype_api.database.crud.update import update_user_email
from genotype_api.database.models import User
from genotype_api.dto.user import UserResponse, UserRequest, PlateOnUser
from genotype_api.exceptions import UserNotFoundError, UserArchiveError, UserExistsError


class UserService:

    def __init__(self, session: Session):
        self.session: Session = session

    @staticmethod
    def _get_plates_on_user(user: User) -> list[PlateOnUser] | None:
        plates_response: list[PlateOnUser] = []
        if not user.plates:
            return None
        for plate in user.plates:
            plate_response = PlateOnUser(
                created_at=plate.created_at,
                plate_id=plate.plate_id,
                id=plate.id,
                signed_by=plate.signed_by,
                signed_at=plate.signed_at,
            )
            plates_response.append(plate_response)
        return plates_response

    def _create_user_response(self, user: User) -> UserResponse:
        plates: list[PlateOnUser] = self._get_plates_on_user(user)
        return UserResponse(email=user.email, name=user.name, id=user.id, plates=plates)

    def create_user(self, user: UserRequest):
        existing_user: User = get_user_by_email(session=self.session, email=user.email)
        if existing_user:
            raise UserExistsError
        new_user: User = create_user(session=self.session, user=user)
        return self._create_user_response(new_user)

    def get_users(self, skip: int, limit: int) -> list[UserResponse]:
        users: list[User] = get_users_with_skip_and_limit(
            session=self.session, skip=skip, limit=limit
        )
        return [self._create_user_response(user) for user in users]

    def get_user(self, user_id: int) -> UserResponse:
        user: User = get_user_by_id(session=self.session, user_id=user_id)
        if not user:
            raise UserNotFoundError
        return self._create_user_response(user)

    def delete_user(self, user_id: int):
        user: User = get_user_by_id(session=self.session, user_id=user_id)
        if not user:
            raise UserNotFoundError
        if user.plates:
            raise UserArchiveError
        delete_user(session=self.session, user=user)

    def update_user_email(self, user_id: int, email: EmailStr):
        user: User = get_user_by_id(session=self.session, user_id=user_id)
        if not user:
            raise UserNotFoundError
        user: User = update_user_email(session=self.session, user=user, email=email)
        return self._create_user_response(user)