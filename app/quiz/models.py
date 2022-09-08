from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class Theme:
    id: Optional[int]
    title: str

    def to_model(self):
        return ThemeModel(title=self.title)


@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]

    def to_model(self):
        answers = [answer.to_model() for answer in self.answers]
        return QuestionModel(title=self.title, theme_id=self.theme_id, answers=answers)


@dataclass
class Answer:
    title: str
    is_correct: bool

    def to_model(self):
        return AnswerModel(title=self.title, is_correct=self.is_correct)


class ThemeModel(db):
    __tablename__ = "themes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)

    def to_dc(self) -> Theme:
        return Theme(id=self.id, title=self.title)


class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)
    theme_id = Column(ForeignKey('themes.id', ondelete='CASCADE'), nullable=False)
    answers = relationship('AnswerModel')

    def to_dc(self):
        return Question(id=self.id, title=self.title, theme_id=self.theme_id,
                        answers=[Answer(title=answer.title,
                                        is_correct=answer.is_correct) for answer in self.answers])


class AnswerModel(db):
    __tablename__ = "answers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)
    is_correct = Column(Boolean, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'),
                         nullable=False)

    def to_dc(self):
        return Answer(title=self.title, is_correct=self.is_correct)
