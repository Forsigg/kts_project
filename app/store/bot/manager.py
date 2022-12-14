import typing
from logging import getLogger

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
                if update.object.peer_id > 2000000000:
                    await self.app.store.vk_api.send_group_message(
                        Message(
                            receiver_id=update.object.peer_id,
                            text=update.object.body,
                        )
                    )
                else:
                    await self.app.store.vk_api.send_message(
                        Message(
                            receiver_id=update.object.user_id,
                            text=update.object.body,
                        )
                    )
