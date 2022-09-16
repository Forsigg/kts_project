from typing import Optional, List

from sqlalchemy import select, and_, update
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.game.game_manager import GameManager
from app.game.models import Game, GameModel, UserModel, User, Score, ScoreModel


class GameAccessor(BaseAccessor):
    ######################################################################
    # GET (SELECT)
    async def get_all_games(self) -> List[Game]:
        async with self.app.database.session.begin() as session:
            query = select(GameModel)
            res = await session.execute(query)
            games = res.scalars().all()
            return [game.to_dc() for game in games]

    async def get_all_game_managers(self) -> List[GameManager]:
        games = await self.get_all_games()
        game_managers = [GameManager(self.app, game) for game in games]
        return game_managers

    async def add_game_managers_to_app(self, *_, **__) -> None:
        self.app.games = await self.get_all_game_managers()

    async def get_game_by_id(self, game_id: int) -> Optional[Game]:
        async with self.app.database.session.begin() as session:
            query = select(GameModel).where(GameModel.id == game_id)
            res = await session.execute(query)
            game = res.scalar()
            if game:
                return game.to_dc()
        return None

    async def get_active_game_by_chat_id(self, chat_id: int) -> Optional[Game]:
        async with self.app.database.session.begin() as session:
            query = select(GameModel).where(and_(
                GameModel.chat_id == chat_id,
                GameModel.state_id < 5
            )).options(joinedload(GameModel.scores))
            res = await session.execute(query)
            game = res.scalar()
            if game:
                return game.to_dc()
        return None

    async def get_score_by_id(self, score_id: int) -> Optional[Score]:
        async with self.app.database.session.begin() as session:
            query = select(ScoreModel).where(ScoreModel.id == score_id)
            res = await session.execute(query)
            score = res.scalar()
            if score:
                return score.to_dc()
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

    async def get_state_id_by_game_id(self, game_id: int) -> Optional[int]:
        async with self.app.database.session.begin() as session:
            game = await self.get_game_by_id(game_id)
            if game is not None:
                return game.state_id
        return None

    ######################################################################
    # CREATE (INSERT)

    async def create_game(self, chat_id: int) -> Game:
        async with self.app.database.session.begin() as session:
            question = await self.app.store.quizzes.get_random_question()
            game = GameModel(chat_id=chat_id, state_id=1, question_id=question.id)
            session.add(game)
        return game.to_dc()

    async def create_user(self, user_id: int, user_full_name: str) -> User:
        async with self.app.database.session.begin() as session:
            user = UserModel(id=user_id, full_name=user_full_name)
            session.add(user)
        return user.to_dc()

    async def create_start_scores(self, game_id: int, users_id: list[int]) -> List[Score]:
        async with self.app.database.session.begin() as session:
            scores = [ScoreModel(
                game_id=game_id,
                user_id=user_id,
                total=0
            ) for user_id in users_id]
            session.add_all(scores)
            return [score.to_dc() for score in scores]

    async def create_start_score(self, game_id: int, user_id: int) -> Score:
        async with self.app.database.session.begin() as session:
            score = ScoreModel(game_id=game_id, user_id=user_id)
            session.add(score)
        return score.to_dc()

    ######################################################################
    # UPDATE

    async def update_total_in_score(self, score_id: int, total: int) -> Score:
        async with self.app.database.session.begin() as session:
            await session.execute(update(ScoreModel).where(ScoreModel.id ==
                                                           score_id).values(
                total=total))
            score = await self.get_score_by_id(score_id)
        return score

    async def add_answer_to_used(self, game_id: int, answer: str) -> Game:
        async with self.app.database.session.begin() as session:
            await session.execute(update(GameModel).where(GameModel.id == game_id).values(
                used_answers=f"{GameModel.used_answers},{answer}"))
            game = await self.get_game_by_id(game_id)
        return game

    async def update_score_to_minus_one_point(self, score_id: int) -> Score:
        async with self.app.database.session.begin() as session:
            await session.execute(update(ScoreModel).where(ScoreModel.id ==
                                                           score_id).values(
                total=0))
            score = await self.get_score_by_id(score_id)
        return score

    async def update_state_in_game(self, game_id: int, state_id: int) -> Game:
        async with self.app.database.session.begin() as session:
            await session.execute(update(GameModel).where(GameModel.id == game_id).values(
                state_id=state_id))
            game = await self.get_game_by_id(game_id)
        return game
