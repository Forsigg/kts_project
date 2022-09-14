from typing import Optional, List

from sqlalchemy import select, update, and_

from app.base.base_accessor import BaseAccessor
from app.game.models import Game, GameModel, UserModel, User, Score, ScoreModel


class GameAccessor(BaseAccessor):
    ######################################################################
    # GET (SELECT)
    async def get_game_by_id(self, game_id: int) -> Optional[Game]:
        async with self.app.database.session.begin() as session:
            query = select(GameModel).where(GameModel.id == game_id)
            res = await session.execute(query)
            game = res.scalar()
            if game:
                return game.to_dc()
        return None

    async def get_active_game_by_chat_id(self, game_id: int) -> Optional[Game]:
        async with self.app.database.session.begin() as session:
            query = select(GameModel).where(and_(
                GameModel.id == game_id,
                GameModel.state_id < 5
            ))
            res = await session.execute(query)
            game = res.scalar()
            if game:
                return game.to_dc()
        return None

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

    ######################################################################
    # CREATE (INSERT)

    async def create_game(self, chat_id: int) -> Game:
        async with self.app.database.session.begin() as session:
            question = self.app.store.quizzes.get_random_question()
            game = GameModel(chat_id=chat_id, state_id=1, question_id=question.id)
            session.add(game)

        return game.to_dc()

    async def create_user(self, user_id: int, user_full_name: str) -> User:
        async with self.app.database.session.begin() as session:
            user = UserModel(id=user_id, full_name=user_full_name)
            session.add(user)
        return user.to_dc()

    async def create_start_score(self, game_id: int, users_id: list[int]) -> List[Score]:
        scores = [ScoreModel(
            game_id=game_id,
            user_id=user_id
        ) for user_id in users_id]
        async with self.app.database.session.begin() as session:
            session.add_all(scores)
        return [score.to_dc() for score in scores]

    ######################################################################
    # UPDATE

    async def add_one_point_to_score(self, score_id: int) -> Score:
        async with self.app.database.session.begin() as session:
            score = select(ScoreModel).where(ScoreModel.id == score_id)
            score.total += 1
            session.commit()
        return score.to_dc()

    async def update_score_to_minus_one_point(self, score_id: int) -> Score:
        async with self.app.database.session.begin() as session:
            score = select(ScoreModel).where(ScoreModel.id == score_id)
            score.total = 0
            session.commit()
        return score.to_dc()

    async def update_state_in_game(self, game_id: int, state_id: int) -> Game:
        async with self.app.database.session.begin() as session:
            game = select(GameModel).where(GameModel.id == game_id)
            game.state_id = state_id
            session.commit()
        return game.to_dc()
