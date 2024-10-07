"""Routes for users"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr
from starlette import status
from starlette.responses import JSONResponse

from genotype_api.database.store import Store, get_store
from genotype_api.dto.user import CurrentUser, UserRequest, UserResponse
from genotype_api.exceptions import UserArchiveError, UserExistsError, UserNotFoundError
from genotype_api.security import get_active_user
from genotype_api.services.endpoint_services.user_service import UserService

router = APIRouter()


def get_user_service(store: Store = Depends(get_store)) -> UserService:
    return UserService(store)


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_active_user),
) -> UserResponse:
    try:
        return await user_service.get_user(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_active_user),
) -> JSONResponse:
    try:
        await user_service.delete_user(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except UserArchiveError:
        HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User previously signed plates, please archive instead",
        )
    return JSONResponse(content=f"Deleted user with id: {user_id}.", status_code=status.HTTP_200_OK)


@router.put("/{user_id}/email", response_model=UserResponse, response_model_exclude={"plates"})
async def change_user_email(
    user_id: int,
    email: EmailStr,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_active_user),
) -> UserResponse:
    try:
        return await user_service.update_user_email(user_id=user_id, email=email)
    except UserNotFoundError:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get("/", response_model=list[UserResponse], response_model_exclude={"plates"})
async def read_users(
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_active_user),
) -> list[UserResponse]:

    return await user_service.get_users(skip=skip, limit=limit)


@router.post("/", response_model=UserResponse, response_model_exclude={"plates"})
async def create_user(
    user: UserRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_active_user),
):
    try:
        return await user_service.create_user(user)
    except UserExistsError:
        HTTPException(status_code=409, detail="Email already registered.")
