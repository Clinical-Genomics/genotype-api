"""Module to holds the user service."""

from pydantic import EmailStr

from genotype_api.database.models import User
from genotype_api.database.store import Store
from genotype_api.dto.user import PlateOnUser, UserRequest, UserResponse
from genotype_api.exceptions import (UserArchiveError, UserExistsError,
                                     UserNotFoundError)
from genotype_api.services.endpoint_services.base_service import BaseService


class UserService(BaseService):

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

    async def create_user(self, user: UserRequest):
        existing_user: User = await self.store.get_user_by_email(email=user.email)
        if existing_user:
            raise UserExistsError
        db_user = User(email=user.email, name=user.name)
        new_user: User = await self.store.create_user(user=db_user)
        return self._create_user_response(new_user)

    async def get_users(self, skip: int, limit: int) -> list[UserResponse]:
        users: list[User] = await self.store.get_users_with_skip_and_limit(skip=skip, limit=limit)
        return [self._create_user_response(user) for user in users]

    async def get_user(self, user_id: int) -> UserResponse:
        user: User = await self.store.get_user_by_id(user_id=user_id)
        if not user:
            raise UserNotFoundError
        return self._create_user_response(user)

    async def delete_user(self, user_id: int):
        user: User = await self.store.get_user_by_id(user_id=user_id)
        if not user:
            raise UserNotFoundError
        if user.plates:
            raise UserArchiveError
        await self.store.delete_user(user=user)

    async def update_user_email(self, user_id: int, email: EmailStr):
        user: User = await self.store.get_user_by_id(user_id=user_id)
        if not user:
            raise UserNotFoundError
        user: User = await self.store.update_user_email(user=user, email=email)
        return self._create_user_response(user)
