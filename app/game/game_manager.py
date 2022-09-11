from typing import Optional, List, TYPE_CHECKING, Tuple
from sqlalchemy.exc import IntegrityError

from app.game.models import User, Score, Game
from app.store.vk_api.dataclasses import Message

if TYPE_CHECKING:
    from app.web.app import Application


class GameManager:
    GAMES: List[Tuple[int, int]] = []
    STATES = ('CREATED', 'WAITING', 'DONE')

    def __init__(self, app: "Application", id_: int = None, chat_id=None):
        if id_ is None:
            self.game: Optional[Game] = None
        else:
            self.app = app
            self.game = self.app.store.games.get_game_by_id(id_)

        self.used_questions = []
        self.state = None
        self.is_active = True
        self.chat_id = chat_id
        self.scores: Optional[List[Score]] = None
        self.users: Optional[List[User]] = None

    async def start_game(self, chat_id: int) -> None:
        self.state = 'CREATED'
        self.chat_id = chat_id
        self.users = await self.app.store.vk_api.get_conversation_members(peer_id=chat_id)
        self.game = await self.app.store.games.create_game()
        self.GAMES.append((self.game.id, self.chat_id))
        for user in self.users:
            try:
                await self.app.store.games.create_user(user.id, user.full_name)
            except IntegrityError:
                pass
        self.scores = await self.app.store.games.create_start_score(
            game_id=self.game.id,
            users_id=[user.id for user in self.users]
        )
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=chat_id,
            text=f'Добрый день! Начинаем игру 100 к 1. Игра № {self.game.id}, участники: '
                 f'{",".join([user.full_name for user in self.users])}'
        ))

    async def send_question(self) -> None:
        # Тут будет логика по получению рандомного вопроса и помещению его в список,
        # чтоб не было повторения
        question = self.app.store.quizzes.get_random_question()
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"{question.title}"
        ))
        self.state = 'WAITING'

    async def add_point(self, user_id: int) -> None:
        pass

    async def end_game(self, chat_id: int):
        self.state = 'DONE'
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=chat_id,
            text=f'Игра закончена, всем до свидания!'
        ))

        await self.app.store.games.change_game_not_active(self.game.id)

        self.GAMES.remove((self.game.id, self.chat_id))
        self.game = None
        self.users = None
        self.scores = None
        self.is_active = False


