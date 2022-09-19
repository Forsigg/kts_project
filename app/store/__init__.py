import typing


from app.store.database.database import Database
from app.store.game.accessor import GameAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.bot.manager import BotManager
        from app.store.admin.accessor import AdminAccessor
        from app.store.quiz.accessor import QuizAccessor
        from app.store.vk_api.accessor import VkApiAccessor

        self.quizzes = QuizAccessor(app)
        self.games = GameAccessor(app)
        self.admins = AdminAccessor(app)
        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
    app.on_startup.append(app.store.admins.create_first_admin)

    app.on_startup.append(app.store.games.add_game_managers_to_app)

