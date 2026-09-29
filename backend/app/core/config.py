"""Application settings, read from environment variables."""

import os
from dataclasses import dataclass

DEFAULT_DATABASE_URL = "sqlite:///./ultimate_tic_tac_toe.db"


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str


def get_settings() -> Settings:
    return Settings(database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
