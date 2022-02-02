"""In production all this stuff happens in frontend."""

from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, Security

import requests
from typing import Optional
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuthFlowAuthorizationCode
from fastapi.security.oauth2 import OAuth2
from sqlmodel import Session
from starlette.requests import Request
from genotype_api.crud.users import get_user_by_email
from genotype_api.database import get_session
from genotype_api.models import User
from genotype_api.config import security_settings
from genotype_api.models import User, Token


class OAuth2AuthorizationCodeBearer(OAuth2):
    def __init__(
        self,
        authorization_url: str,
        token_url: str,
        client_id: str = None,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):

        flows = OAuthFlowsModel(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl=authorization_url, tokenUrl=token_url, scopes=scopes
            )
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code="401",
                    detail="Unauthorized",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorization_url=security_settings.authorization_url,
    token_url=security_settings.token_url,
    client_id=security_settings.client_id,
    scopes={"openid": "openid", "email": "email", "profile": "profile"},
)


def create_id_token(data: dict, expires_delta: timedelta = None):
    """For development - Creating an id token from google user info. Using specific algorithm, and secret key"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode["exp"] = expire
    return jwt.encode(
        to_encode, security_settings.secret_key, algorithm=security_settings.algorithm
    )


async def get_login_user(
    authorization_token: str = Security(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Optional[User]:
    """For development- getting user info from authorization_token"""
    req = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {authorization_token}"},
    )

    req_data = req.json()
    user: User = get_user_by_email(session=session, email=req_data.get("email"))
    return user


async def get_login_active_user(current_user: User = Depends(get_login_user)):
    """For development"""
    # if current_user.disabled:
    #    raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_id_token(current_user: User = Depends(get_login_user)):
    """For development etc"""
    # if current_user.disabled:
    #    raise HTTPException(status_code=400, detail="Inactive user")
    return Token(id_token=create_id_token(current_user.dict()), token_type="bearer")
