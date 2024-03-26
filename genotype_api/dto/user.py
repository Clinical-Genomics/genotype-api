"""Module for the plate DTOs."""

from pydantic import BaseModel, EmailStr

from genotype_api.dto.plate import PlateResponse


class UserResponse(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    id: int | None = None
    plates: list[PlateResponse] | None = None


class UserRequest(BaseModel):
    email: EmailStr
    name: str
