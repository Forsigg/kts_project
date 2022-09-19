import enum
from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class StateEnum(enum.Enum):
    started = 1
    question = 2
    waiting = 3
    checking = 4
    done = 5


@dataclass
class User:
    id: int
    full_name: str = None


@dataclass
class Score:
    id: int
    game_id: int
    user_id: int
    total: int


@dataclass
class Game:
    id: int
    chat_id: int
    question_id: int
    state_id: int
    used_answers: str


class StateModel(db):
    __tablename__ = "states"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)


class UserModel(db):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=True)

    def to_dc(self):
        return User(id=self.id, full_name=self.full_name)


class ScoreModel(db):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )

    total = Column(Integer, default=0)

    def to_dc(self):
        return Score(
            id=self.id,
            game_id=self.game_id,

            user_id=self.user_id,

            total=self.total,
        )


class GameModel(db):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, nullable=False)
    scores = relationship(ScoreModel, lazy="subquery")
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False, default=1)
    used_answers = Column(String, nullable=True)

    def to_dc(self):

        return Game(
            id=self.id,
            chat_id=self.chat_id,
            question_id=self.question_id,
            state_id=self.state_id,
            used_answers=self.used_answers,
        )

