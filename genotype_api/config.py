from pathlib import Path

from pydantic_settings import BaseSettings

from genotype_api.clients.authentication.keycloak_client import KeycloakClient

GENOTYPE_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = GENOTYPE_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"


class DBSettings(BaseSettings):
    """Settings for serving the genotype-api app"""

    db_uri: str = "mysql+aiomysql://username:password@localhost/dbname"
    db_name: str = "database.db"
    host: str = "localhost"
    port: int = 8000
    echo_sql: bool = False
    max_retries: int = 5
    retry_delay: int = 120  # 2 minutes

    class Config:
        env_file = str(ENV_FILE)


class SecuritySettings(BaseSettings):
    """Settings for serving the genotype-api app"""

    keycloak_client_id: str = "client_id"
    keycloak_client_secret: str = "client_secret"
    keycloak_server_url: str = "server_url"
    keycloak_realm_name: str = "realm_name"
    keycloak_redirect_uri: str = "redirect_uri"
    api_root_path: str = "/"

    class Config:
        env_file = str(ENV_FILE)


security_settings = SecuritySettings()

settings = DBSettings()

keycloak_client = KeycloakClient(
    server_url=security_settings.keycloak_server_url,
    client_id=security_settings.keycloak_client_id,
    client_secret_key=security_settings.keycloak_client_secret,
    realm_name=security_settings.keycloak_realm_name,
    redirect_uri=security_settings.keycloak_redirect_uri,
)
