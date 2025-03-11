import pytest

from genotype_api.models import DecodingResponse, RealmAccess


@pytest.fixture
def realm_access() -> RealmAccess:
    return RealmAccess(roles=["cg-employee"])



@pytest.fixture
def decode_token_response(realm_access) -> DecodingResponse:
    return DecodingResponse(
        exp=1672531199,
        iat=1672531199,
        auth_time=1672531199,
        jti="unique-jti",
        iss="https://issuer.example.com",
        sub="subject-id",
        typ="Bearer",
        azp="client-id",
        sid="session-id",
        acr="1",
        allowed_origins=["https://allowed.example.com"],
        realm_access=realm_access,
        scope="email profile",
        email_verified=True,
        name="John Doe",
        preferred_username="johndoe",
        given_name="John",
        family_name="Doe",
        email="johndoe@example.com",
    )
