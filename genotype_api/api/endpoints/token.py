"""This endpoint id for development only"""

from genotype_api.models import User, Token
from fastapi import APIRouter, Depends, Request
from genotype_api.security_dev import get_login_active_user, create_id_token

router = APIRouter()


@router.get("/", tags=["security"])
async def token(request: Request, current_user: User = Depends(get_login_active_user)):
    return Token(id_token=create_id_token(current_user.dict()), token_type="bearer")
