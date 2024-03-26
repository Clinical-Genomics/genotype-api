"""Module for the plate DTOs."""

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    id: int | None = None


class UserRequest(BaseModel):
    email: EmailStr
    name: str
