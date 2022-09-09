from dataclasses import dataclass
from sqlalchemy import Column, Integer, ForeignKey, Boolean, String

from app.store.database.sqlalchemy_base import db


@dataclass
class User:
    id: int
    full_name: str


@dataclass
class Score:
    id: int
    game_id: int
    player: User
    total: int


@dataclass
class Game:
    id: int
    is_active: bool


class UserModel(db):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)

    def to_dc(self):
        return User(id=self.id, full_name=self.full_name)


class ScoreModel(db):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    total = Column(Integer, default=0)

    def to_dc(self):
        return Score(id=self.id, game_id=self.game_id, player=User(
            id=self.user_id
        ), total=self.total)


class GameModel(db):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, nullable=False, default=False)

    def to_dc(self):
        return Game(id=self.id, is_active=self.is_active)


class UsersGamesModel(db):
    __tablename__ = 'users_games'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)


