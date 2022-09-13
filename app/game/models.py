import enum
from dataclasses import dataclass
from typing import List

from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, Enum
from sqlalchemy.orm import relationship

from app.quiz.schemes import Question
from app.store.database.sqlalchemy_base import db


@dataclass
class StateEnum(enum.Enum):
    pass


@dataclass
class User:
    id: int
    full_name: str = None


@dataclass
class Score:
    id: int
    game_id: int
    player: User
    total: int


@dataclass
class Game:
    id: int
    chat_id: int
    scores: List[Score]
    question: Question
    state: StateEnum



class UserModel(db):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=True)

    def to_dc(self):
        return User(id=self.id, full_name=self.full_name)


class ScoreModel(db):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total = Column(Integer, default=0)

    def to_dc(self):
        return Score(
            id=self.id,
            game_id=self.game_id,
            player=User(id=self.user_id),
            total=self.total,
        )


class GameModel(db):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, nullable=False, default=False)

    def to_dc(self):
        return Game(id=self.id, is_active=self.is_active)


class UsersGamesModel(db):
    __tablename__ = "users_games"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )

#
# class StateModel(db):
#     __tablename__ = 'states'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     game_id = Column(Integer, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
#     question_id = Column(Integer, ForeignKey('questions.id'), nullable=True)
#     chat_id = Column(Integer, nullable=False)
#     scores = relationship("scores")
#     users = relationship('users')
#     state = Column(String, nullable=False)
#
