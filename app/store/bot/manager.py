import typing
from logging import getLogger

from app.game.game_manager import GameManager
from app.quiz.schemes import Answer
from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def bot_start_game(self, chat_id: int):
        game = await self.is_game_exist(chat_id)
        if game:
            return await self.app.store.vk_api.send_group_message(
                Message(
                    receiver_id=chat_id,
                    text='Игра еще не закончена. Чтобы закончить игру введите "закончить игру"',
                )
            )

        game = GameManager(self.app)
        self.app.games.append(game)
        await game.start_game(chat_id)

    async def is_game_exist(self, chat_id) -> typing.Union[bool, GameManager]:
        if self.app.games:
            game_filter = list(filter(lambda x: x.chat_id == chat_id, self.app.games))
            if game_filter:
                return game_filter[0]
        return False

    async def bot_end_game(self, chat_id: int):
        game = await self.is_game_exist(chat_id)
        if not game:
            return await self.app.store.vk_api.send_group_message(
                Message(
                    receiver_id=chat_id,
                    text="Игра еще не начата.",
                )
            )

        await game.end_game(chat_id)

    async def is_ready_to_answer(self, chat_id: int) -> bool:
        game = await self.is_game_exist(chat_id)
        if game:
            if game.state == "CHECKING":
                return True
            return False

    async def handle_updates(self, updates: list[Update]):
        # TODO: перенести основную логику игры в GameManager
        if updates:
            for update in updates:
                user_id = update.object.user_id
                message = update.object
                message_text = message.body.lower()
                chat_id = message.peer_id
                if chat_id > 2000000000:

                    game = await self.app.store.games.get_active_game_by_chat_id()

                    if message_text == "начать игру" and game is None:
                        await self.bot_start_game(chat_id)

                    elif message_text == 'закончить игру' and game:
                        await self.bot_end_game(chat_id)

                    elif message_text == 'ответ' and not await self.is_ready_to_answer(chat_id):
                        if await game.is_user_kicked(user_id):
                            pass
                        else:
                            game.state = "CHECKING"

                    elif await self.is_ready_to_answer(message.peer_id):
                        if not game.is_user_kicked(user_id):
                            answer = Answer(title=message_text)
                            if await game.is_correct_answer(answer):
                                await game.add_point(user_id)
                            else:
                                await game.user_kick(user_id)



