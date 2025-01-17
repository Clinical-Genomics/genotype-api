import requests
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from starlette import status
from starlette.requests import Request

from genotype_api.config import security_settings
from genotype_api.database.models import User
from genotype_api.database.store import Store, get_store
from genotype_api.dto.user import CurrentUser


def decode_id_token(token: str):
    try:
        payload = jwt.decode(
            token,
            key=requests.get(security_settings.jwks_uri).json(),
            algorithms=[security_settings.algorithm],
            audience=security_settings.client_id,
            options={
                "verify_at_hash": False,
            },
        )
        return payload
    except jwt.JWTError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.",
            )
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme.",
            )
        payload = self.verify_jwt(credentials.credentials)
        return {"token": credentials.credentials, "payload": payload}

    def verify_jwt(self, jwtoken: str) -> dict | None:
        try:
            payload = decode_id_token(jwtoken)
            if payload and "email" in payload:
                return {"email": payload["email"]}
            else:
                return None
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token or expired token.",
            )


jwt_scheme = JWTBearer()


async def get_active_user(
    token_info: dict = Security(jwt_scheme),
    store: Store = Depends(get_store),
) -> CurrentUser:
    """Dependency for secure endpoints"""

    if token_info is None or not isinstance(token_info, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    payload = token_info.get("payload")
    if not payload or "email" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_email = token_info["payload"]["email"]
    db_user: User = await store.get_user_by_email(email=user_email)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in DB")
    return CurrentUser(
        id=db_user.id,
        email=db_user.email,
        name=db_user.name,
    )
