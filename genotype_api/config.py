from pathlib import Path
from typing import Literal

from pydantic import BaseSettings

GENOTYPE_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = GENOTYPE_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"


class DBSettings(BaseSettings):
    """Settings for serving the genotype-api app"""

    db_uri: str = "sqlite:///database.db"
    db_name: str = "database.db"
    host: str = "localhost"
    port: int = 8000

    class Config:
        env_file = str(ENV_FILE)


class SecuritySettings(BaseSettings):
    """Settings for serving the genotype-api app"""

    client_id = ""
    algorithm = ""
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"

    class Config:
        env_file = str(ENV_FILE)


security_settings = SecuritySettings()

settings = DBSettings()
