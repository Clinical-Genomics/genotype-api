from pathlib import Path

from pydantic import BaseSettings

GENOTYPE_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = GENOTYPE_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"


class Settings(BaseSettings):
    """Settings for serving the genotype-api app"""

    db_uri: str = "sqlite:///database.db"
    db_name: str = "database.db"
    host: str = "localhost"
    port: int = 8000

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()


print(settings.dict())
