"""Persistence models.

Only the moves are stored. Whose turn it is, which board is active, who won each small board,
and who won the game are all derived from the move list (see ``app.services.rules``).
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, UTCDateTime, utc_now


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)

    moves: Mapped[list["Move"]] = relationship(
        back_populates="game",
        order_by="Move.sequence",
        cascade="all, delete-orphan",
    )


class Move(Base):
    __tablename__ = "moves"
    __table_args__ = (
        UniqueConstraint("game_id", "sequence"),
        UniqueConstraint("game_id", "board", "cell"),
        CheckConstraint("board BETWEEN 0 AND 8", name="board_range"),
        CheckConstraint("cell BETWEEN 0 AND 8", name="cell_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    # 0-based position in the game. Even sequences are X, odd are O.
    sequence: Mapped[int]
    board: Mapped[int]
    cell: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)

    game: Mapped[Game] = relationship(back_populates="moves")
