"""Module for the plate DTOs."""

from pydantic import BaseModel, EmailStr


class UserInfoResponse(BaseModel):
    email: EmailStr
    name: str | None = None
    id: int
