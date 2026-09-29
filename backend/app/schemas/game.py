"""Request and response bodies for the games API."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BoardStatus, GameStatus, Player
from app.services.game_service import GameView

Index = Annotated[int, Field(ge=0, le=8, strict=True)]


class ErrorResponse(BaseModel):
    code: str = Field(examples=["wrong_board"])
    detail: str = Field(examples=["This move must be played in board 4."])


class MoveCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    board: Index = Field(description="Small board, 0-8, left to right then top to bottom.")
    cell: Index = Field(description="Square within that board, 0-8, same ordering.")


class MoveRead(BaseModel):
    sequence: int
    board: int
    cell: int
    player: Player
    created_at: datetime


class SmallBoardRead(BaseModel):
    index: int
    cells: list[Player | None]
    status: BoardStatus
    winner: Player | None
    playable: bool = Field(description="Whether the next move may be played in this board.")


class GameRead(BaseModel):
    id: int
    created_at: datetime
    status: GameStatus
    winner: Player | None
    current_player: Player | None
    active_board: int | None = Field(
        description="The board the next move must go in, or null when any open board is allowed."
    )
    boards: list[SmallBoardRead]
    moves: list[MoveRead]

    @classmethod
    def from_view(cls, view: GameView) -> "GameRead":
        state = view.state
        return cls(
            id=view.id,
            created_at=view.created_at,
            status=state.status,
            winner=state.winner,
            current_player=state.current_player,
            active_board=state.active_board,
            boards=[
                SmallBoardRead(
                    index=index,
                    cells=list(board.cells),
                    status=board.status,
                    winner=board.winner,
                    playable=state.is_board_playable(index),
                )
                for index, board in enumerate(state.boards)
            ],
            moves=[
                MoveRead(
                    sequence=move.sequence,
                    board=move.board,
                    cell=move.cell,
                    player=move.player,
                    created_at=move.created_at,
                )
                for move in view.moves
            ],
        )
