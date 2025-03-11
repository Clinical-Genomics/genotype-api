from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from starlette import status
from starlette.requests import Request

from genotype_api.config import security_settings, keycloak_client
from genotype_api.database.models import User
from genotype_api.database.store import Store, get_store
from genotype_api.dto.user import CurrentUser

from genotype_api.exceptions import AuthenticationError
from genotype_api.services.authentication.service import AuthenticationService


class JWTBearer(HTTPBearer):
    def __init__(self, auth_service: AuthenticationService, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.auth_service = auth_service

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
            payload: dict = self.auth_service.verify_token(jwtoken).model_dump()
            if payload and "email" in payload:
                return {"email": payload["email"]}
            else:
                return None
        except AuthenticationError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{error}",
            )


auth_service = AuthenticationService(
    redirect_uri=security_settings.keycloak_redirect_uri,
    keycloak_client=keycloak_client,
)
jwt_scheme = JWTBearer(auth_service=auth_service)


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
