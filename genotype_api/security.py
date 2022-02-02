import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from starlette.requests import Request

from genotype_api.database import get_session
from genotype_api.models import User
from genotype_api.config import security_settings
from genotype_api.crud.users import get_user_by_email
from genotype_api.security_dev import get_id_token, get_login_user


def decode_id_token(token: str):
    try:
        return jwt.decode(
            token,
            security_settings.secret_key,
            algorithms=[security_settings.algorithm],
        )
    except:
        return


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=403, detail="Invalid token or expired token.")
        return credentials.credentials

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_id_token(jwtoken)
        except:
            payload = None
        return payload


jwt_scheme = JWTBearer()


async def get_active_user(
    token: str = Security(jwt_scheme),
    session: Session = Depends(get_session),
):
    """Dependency for secure endpoints"""
    user = User.parse_obj(decode_id_token(token))
    db_user: User = get_user_by_email(session=session, email=user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not in DB")
    return user


async def get_user_final(
    token_id: str = Depends(get_login_user),
):
    """Dependency for secure endpoints"""
    return get_active_user(token=token_id)
