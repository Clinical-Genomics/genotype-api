from genotype_api.clients.authentication.keycloak_client import KeycloakClient
from genotype_api.exceptions import AuthenticationError, UserRoleError
from genotype_api.models import DecodingResponse


class AuthenticationService:
    """Authentication service to verify tokens against Keycloak and return user information."""

    def __init__(
        self,
        redirect_uri: str,
        keycloak_client: KeycloakClient,
    ):
        """Initialize the AuthenticationService

        Args:
            redirect_uri: Redirect uri for keycloak
            keycloak_client: KeycloakOpenID client.
        """
        self.redirect_uri = redirect_uri
        self.client = keycloak_client

    def verify_token(self, jwt_token: str) -> DecodingResponse:
        """Verify the token and user role.
        Args:
            token (str): The token to verify.

        Returns:
            Decoded token payload

        Raises:
            AuthenticationError: if an error occured the authentication
        """
        try:
            decoded_token = DecodingResponse(**self.client.decode_token(jwt_token))
            self.check_role(decoded_token.realm_access.roles)
            return decoded_token
        except Exception as error:
            raise AuthenticationError(f"An error occured during authorisation: {error}")

    @staticmethod
    def check_role(roles: list[str]) -> None:
        """Check the user roles.
        Currently set to a single permissable role, expand if needed.
        Args:
            roles (list[str]): The user roles received from the RealmAccess.
        Raises:
            UserRoleError: if required role not present
        """
        if not "cg-employee" in roles:
            raise UserRoleError("The user does not have the required role to access this service.")
