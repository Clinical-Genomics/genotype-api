import pytest
from unittest.mock import MagicMock
from keycloak import KeycloakOpenID

from genotype_api.exceptions import AuthenticationError, UserRoleError
from genotype_api.models import DecodingResponse
from genotype_api.services.authentication.service import AuthenticationService


def test_verify_token_success(decode_token_response):

    # GIVEN a mock user service and a keycloak client
    mock_keycloak_client = MagicMock(spec=KeycloakOpenID)

    # GIVEN mocked responses from the services
    mock_keycloak_client.decode_token.return_value = decode_token_response.dict()


    # GIVEN an AuthenticationService
    auth_service = AuthenticationService(
        redirect_uri="redirect_uri",
        keycloak_client=mock_keycloak_client,
    )

    # WHEN verifying a jwt token
    decoded_token: DecodingResponse = auth_service.verify_token("jwt_token")

    # THEN the token is verified and a user with the email is returned
    assert decoded_token.email == decode_token_response.email
    mock_keycloak_client.decode_token.assert_called_once_with("jwt_token")


def test_verify_token_invalid_role(decode_token_response):
    # GIVEN a mock user service and a keycloak client
    mock_keycloak_client = MagicMock(spec=KeycloakOpenID)

    # GIVEN a decoded token response with an invalid user role
    decode_token_response.realm_access.roles = ["invalid-role"]
    mock_keycloak_client.decode_token.return_value = decode_token_response.dict()

    # GIVEN an AuthenticationService
    auth_service = AuthenticationService(
        redirect_uri="redirect_uri",
        keycloak_client=mock_keycloak_client,
    )

    # WHEN verifying the jwt token

    # THEN an UserRoleError is raised
    with pytest.raises(
        AuthenticationError, match="The user does not have the required role to access this service."
    ):
        auth_service.verify_token("jwt_token")