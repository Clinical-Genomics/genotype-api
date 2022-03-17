from typing import Optional

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from starlette import status

from starlette.requests import Request

from genotype_api.database import get_session
from genotype_api.models import User
from genotype_api.config import security_settings
from genotype_api.crud.users import get_user_by_email
from jose import jwt
import requests


def decode_id_token(token: str):

    payload = jwt.decode(
        token,
        key=requests.get(security_settings.jwks_uri).json(),
        algorithms=[security_settings.algorithm],
        audience=security_settings.client_id,
        options={
            "verify_at_hash": False,
        },
    )
    if not payload:
        return jwt.get_unverified_claims(token)
    return payload


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code."
            )
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme."
            )
        self.verify_jwt(credentials.credentials)

        return credentials.credentials

    def verify_jwt(self, jwtoken: str) -> Optional[dict]:
        try:
            return decode_id_token(jwtoken)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token."
            )


jwt_scheme = JWTBearer()


async def get_active_user(
    token: str = Security(jwt_scheme),
    session: Session = Depends(get_session),
):
    """Dependency for secure endpoints"""
    user = User.parse_obj(decode_id_token(token))
    db_user: User = get_user_by_email(session=session, email=user.email)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in DB")
    return user
