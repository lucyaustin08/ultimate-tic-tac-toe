"""The Alembic migrations must build exactly the schema the models describe."""

import json
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext

import app.models.game  # noqa: F401  (registers the tables)
from app import openapi_export
from app.core.database import Base, build_engine

BACKEND_DIR = Path(__file__).resolve().parent.parent


def test_migrations_match_the_models(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", url)

    command.upgrade(config, "head")

    engine = build_engine(url)
    with engine.connect() as connection:
        differences = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    engine.dispose()
    assert differences == []


def test_openapi_export_prints_the_games_api(capsys: pytest.CaptureFixture[str]) -> None:
    openapi_export.main()
    schema = json.loads(capsys.readouterr().out)
    assert "/api/v1/games/{game_id}/moves" in schema["paths"]
    assert "ErrorResponse" in schema["components"]["schemas"]
