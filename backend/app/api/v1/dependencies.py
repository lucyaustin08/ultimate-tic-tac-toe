from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.repositories.game_repository import GameRepository
from app.services.game_service import GameService


def get_game_service(session: Annotated[Session, Depends(get_session)]) -> GameService:
    return GameService(GameRepository(session))


GameServiceDep = Annotated[GameService, Depends(get_game_service)]
