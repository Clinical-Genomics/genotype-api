from pathlib import Path

from pydantic_settings import BaseSettings

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

    client_id: str = ""
    algorithm: str = ""
    jwks_uri: str = "https://www.googleapis.com/oauth2/v3/certs"
    api_root_path: str = "/"

    class Config:
        env_file = str(ENV_FILE)


security_settings = SecuritySettings()

settings = DBSettings()
