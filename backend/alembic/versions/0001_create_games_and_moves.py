"""create games and moves

Revision ID: 0001
Revises:
Create Date: 2026-09-29 09:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

import app.core.database

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", app.core.database.UTCDateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_games")),
    )
    op.create_table(
        "moves",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("board", sa.Integer(), nullable=False),
        sa.Column("cell", sa.Integer(), nullable=False),
        sa.Column("created_at", app.core.database.UTCDateTime(), nullable=False),
        sa.CheckConstraint("board BETWEEN 0 AND 8", name=op.f("ck_moves_board_range")),
        sa.CheckConstraint("cell BETWEEN 0 AND 8", name=op.f("ck_moves_cell_range")),
        sa.ForeignKeyConstraint(
            ["game_id"], ["games.id"], name=op.f("fk_moves_game_id_games")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_moves")),
        sa.UniqueConstraint("game_id", "sequence", name=op.f("uq_moves_game_id_sequence")),
        sa.UniqueConstraint(
            "game_id", "board", "cell", name=op.f("uq_moves_game_id_board_cell")
        ),
    )


def downgrade() -> None:
    op.drop_table("moves")
    op.drop_table("games")
