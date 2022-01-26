import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from starlette.requests import Request
from genotype_api.models import User
from genotype_api.config import security_settings


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


async def get_active_user(token: str = Security(jwt_scheme)):
    """Dependency for secure endpoints"""
    # if user.disabled:
    # raise HTTPException(status_code=400, detail="Inactive user")
    return User.parse_obj(decode_id_token(token))
