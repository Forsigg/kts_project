import typing
from logging import getLogger

from app.game.game_manager import GameManager
from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        if updates:
            for update in updates:
                print(update)
                message = update.object
                if message.peer_id > 2000000000:
                    if message.body.lower() == "начать игру":
                        game = GameManager(self.app)
                        await game.start_game(message.peer_id)

                    if message.body.lower() == 'закончить игру':
                        game = GameManager(self.app, chat_id=message.peer_id)
                        await game.end_game(message.peer_id)
                    else:
                        await self.app.store.vk_api.send_group_message(
                            Message(
                                receiver_id=update.object.peer_id,
                                text=update.object.body,
                            )
                        )
                else:
                    await self.app.store.vk_api.send_message(
                        Message(
                            receiver_id=message.user_id,
                            text=message.body,
                        )
                    )
