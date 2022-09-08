from typing import Optional, List

from sqlalchemy import select, update

from app.base.base_accessor import BaseAccessor
from app.game.models import Game, GameModel, UserModel, User, Score, ScoreModel


class GameAccessor(BaseAccessor):
    async def get_game_by_id(self, game_id: int) -> Optional[Game]:
        async with self.app.database.session.begin() as session:
            query = select(GameModel).where(GameModel.id == game_id)
            res = await session.execute(query)
            game = res.scalar()
            if game:
                return game.to_dc()
        return None

    async def create_game(self) -> Game:
        async with self.app.database.session.begin() as session:
            game = GameModel(is_active=True)
            session.add(game)

        return game.to_dc()

    async def change_game_is_active(self, game_id: int) -> None:
        async with self.app.database.session.begin() as session:
            pass
            # query = update(GameModel).where(GameModel.id == game_id).values(is_active=)

    async def create_user(self, user_id: int) -> User:
        async with self.app.database.session.begin() as session:
            user = UserModel(id=user_id)
            session.add(user)
        return user.to_dc()

    async def get_scores_by_game_id(self, game_id: int) -> List[Score]:
        async with self.app.database.session.begin() as session:
            query = select(ScoreModel).where(ScoreModel.game_id == game_id)
            res = await session.execute(query)
            scores = res.scalars().all()
            scores = [score.to_dc() for score in scores]
        return scores

    async def get_scores_by_user_id(self, user_id: int) -> List[Score]:
        async with self.app.database.session.begin() as session:
            query = select(ScoreModel).where(ScoreModel.user_id == user_id)
            res = await session.execute(query)
            scores = res.scalars().all()
            scores = [score.to_dc() for score in scores]
        return scores
