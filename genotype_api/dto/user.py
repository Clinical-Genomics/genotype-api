"""Module for the plate DTOs."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class PlateOnUser(BaseModel):
    created_at: datetime | None = None
    plate_id: int | None = None
    signed_by: int | None = None
    signed_at: datetime | None = None
    id: str | None = None


class UserResponse(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    id: int | None = None
    plates: list[PlateOnUser] | None = None


class UserRequest(BaseModel):
    email: EmailStr
    name: str


class CurrentUser(BaseModel):
    id: int
    email: EmailStr
    name: str
