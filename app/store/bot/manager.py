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

    async def bot_start_game(self, chat_id: int) -> GameManager:
        game = await self.app.store.games.get_active_game_by_chat_id(chat_id)
        if game:
            await self.app.store.vk_api.send_group_message(
                Message(
                    receiver_id=chat_id,
                    text='Игра еще не закончена. Чтобы закончить игру введите "закончить игру"',
                )
            )
            game = GameManager(self.app, game)
            if game not in self.app.games:
                self.app.games.append(game)
            return game
        else:
            game = GameManager(self.app)
            self.app.games.append(game)
            await game.start_game(chat_id)
            return game

    def get_existed_game_or_get_false(self, chat_id) -> typing.Union[bool, GameManager]:
        if self.app.games:
            game_filter = list(filter(lambda x: x.chat_id == chat_id, self.app.games))
            if game_filter:
                return game_filter[0]
        return False

    async def bot_end_game(self, chat_id: int):
        game_manager = self.get_existed_game_or_get_false(chat_id=chat_id)
        if not game_manager:
            return await self.app.store.vk_api.send_group_message(
                Message(
                    receiver_id=chat_id,
                    text="Игра еще не начата.",
                )
            )

        await game_manager.end_game(chat_id)

    async def handle_updates(self, updates: list[Update]):
        if updates:
            for update in updates:
                user_id = update.object.user_id
                message = update.object
                message_text = message.body.lower()
                chat_id = message.peer_id
                if chat_id > 2000000000:

                    game = await self.app.store.games.get_active_game_by_chat_id(
                        chat_id

                    )
                    game_manager = self.get_existed_game_or_get_false(chat_id=chat_id)

                    if (
                        game
                        and game_manager
                        and (
                            await game_manager.is_all_users_kicked()
                            or await game_manager.is_all_answers_used()
                        )
                    ):
                        await game_manager.end_game(chat_id)

                    if message_text == "начать игру":
                        game_manager = await self.bot_start_game(chat_id)
                        game = await self.app.store.games.get_active_game_by_chat_id(
                            chat_id
                        )
                        if game.state_id == 2:
                            await game_manager.send_question()

                    elif message_text == "закончить игру" and game is not None:
                        await self.bot_end_game(chat_id)

                    elif (
                        message_text == "ответ" and game.state_id == 3
                    ):  # 3 state = "waiting"
                        if await game_manager.is_user_kicked(user_id):
                            pass
                        else:
                            await game_manager.prepare_to_answer(user_id)
                            await self.app.store.games.update_state_in_game(
                                game_id=game.id, state_id=4
                            )
                            game.state = GameManager.STATES[4]

                    elif game and game.state_id == 4:  # 4 state = "checking"
                        if not await game_manager.is_user_kicked(user_id):
                            answer = Answer(title=message_text)
                            await game_manager.check_answer(
                                answer=answer, user_id=user_id
                            )
