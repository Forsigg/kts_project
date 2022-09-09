from typing import Optional, List, TYPE_CHECKING

from app.game.models import Game, User, Score
from app.store.vk_api.dataclasses import Message

if TYPE_CHECKING:
    from app.web.app import Application


class GameManager:
    def __init__(self, app: "Application"):
        self.game = Optional[Game] = None
        self.users = Optional[List[User]] = None
        self.app = app
        self.scores = Optional[List[Score]] = None
        self.chat_id: Optional[int] = None

    async def start_game(self, chat_id: int):
        #TODO: доделать функцию старта игры
        self.chat_id = chat_id
        self.users = await self.app.store.vk_api.get_conversation_members(peer_id=chat_id)
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=chat_id,
            text=f'Добрый день! Начинаем игру 100 к 1, участники: {",".join([user.id for user in self.users])}'
        ))
