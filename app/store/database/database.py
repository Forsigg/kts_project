from typing import Optional, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.store.database.sqlalchemy_base import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self,  *_: list, **__: dict) -> None:
        self._db = db
        db_user = self.app.config.database.user
        db_password = self.app.config.database.password
        db_port = self.app.config.database.port
        db_name = self.app.config.database.database
        self._engine = create_async_engine(f"postgresql+asyncpg://{db_user}:"
                                           f"{db_password}@localhost:"
                                           f"{db_port}/{db_name}",
                                           future=True)

        self.session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)

        # first admin check
        admin_from_db = await self.app.store.admins.get_by_email(self.app.config.admin.email)
        if admin_from_db is None:
            await self.app.store.admins.create_admin(
                email=self.app.config.admin.email,
                password=self.app.config.admin.password)
            print('first admin created')

        print('database connected')

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self._engine:
            await self._engine.dispose()
        self._db = None
